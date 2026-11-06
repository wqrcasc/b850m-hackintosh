# 探索纪实：一个通宵，从「不可能」到桌面

> 这篇不是教程，是**过程记录**。
> 教程在 [02-可复现步骤.md](02-可复现步骤.md)，想直接动手的可以跳过这里。
> 但如果你想理解「为什么一块 2026 年的 B850 主板会把 macOS 卡死在 PCI 枚举」——
> 这里面每一步失败都有它的意义。

---

## 00. 起点

事情开始于一句很普通的话：

> 「本机可以装 macOS 吗？」

机器是台挺新的 AM5 主机：7800X3D、七彩虹 B850M、RTX 5070 Ti。
按 2020 年的黑苹果常识，这三个部件每一个都是红灯：

- **AMD CPU**：要打内核补丁（AMD Vanilla），能跑但麻烦
- **NVIDIA 新卡**：macOS 早就没有 N 卡驱动了
- **B850 芯片组**：2025 年的板子，社区几乎没有案例

但 2026 年有两件事变了：

1. **NullMoth** 项目给 Turing 以后的 N 卡写了 Metal 驱动（走 NVK/Mesa 翻译），5070 Ti 有救了
2. macOS 26 Tahoe 是**最后一个支持 x86 的版本**——再不上车就没机会了

于是决定：试试。

---

## 01. 第一条路：虚拟机（成功，但不够）

最稳的起点永远是虚拟机。VMware + OC4VM 模板，一个下午就装好了 Tahoe。

**它证明了三件事：**

- macOS 26 能在这颗 7800X3D 上跑
- AMD Vanilla 补丁没问题
- 我手上的安装镜像是好的

**但它也暴露了天花板：**

- 没有 Metal，VMware 的 SVGA 只有 2D 加速
- 界面卡、滚动涩、视频打不开
- 5070 Ti 完全用不上

虚拟机像一张「证明书」：**这台机器的计算部分能跑 macOS，跑不动的只是这块主板的固件。**

---

## 02. 第二条路：实体机，撞墙

用 1401 做启动盘（它会把 OpenCore、NullMoth 参数、恢复镜像全部写好），F11 引导。

结果：

```
Apple 标志出现 → 内核开始跑 → 停在 CoreAnalyticsHub start completed
→ USB 全部失效（键盘灯灭）→ 永远不动
```

**关键细节：USB 和 PCI 是同一个芯片组管的。**
两个总线同时死，说明不是某个驱动崩了，是**整个 PCH 停止响应**。
内核没有 panic——它发了一个请求，然后那个请求再也没有回来。

### 排查过程（全部失败）

| 试过 | 结果 |
|---|---|
| 换 OpenCore 版本（1.0.8 / 1401 的 REL-107） | 同一行 |
| macOS 26 / Sequoia 15 | 同一行 |
| 拔掉 5070 Ti，只用核显 | 同一行 |
| 8 核 → `cpus=1` | 从「瞬间复位」变成「卡住」 |
| BIOS 1004 → 1010（2026-09 新版，换了一代 AGESA） | 同一行 |
| Above 4G 开/关 + `npci=0x2000` | 同一行 |
| `DevirtualiseMmio` 开/关 | 只影响更早的 0x16 错误 |

论坛上翻到一个几乎一样的案例：**ASUS B850 + 9950X3D，卡在同一个 `AMDCPUSupport::start trying to init PCI service`**。
那个人后来**刷回旧 BIOS 就好了**。

问题是：**七彩虹这块板只有一版 BIOS（1004），刷不了旧的。**

到这里，按常理该放弃了。

---

## 03. 转折：把主板的 ACPI 挖出来

放弃之前，我决定看一眼「固件到底给系统描述了什么」。

### 3.1 从 Windows 里把 ACPI 表挖出来

不用装任何工具，Windows 内核本身就缓存了全部 ACPI 表：

```powershell
# GetSystemFirmwareTable / EnumSystemFirmwareTables 两个 API
# 或者直接读注册表 HKLM\HARDWARE\ACPI\DSDT\...
```

再把 `acpidump.exe`（ACPICA 自带）跑一遍——它比 Windows 的枚举 API **多 dump 出两张表**。

其中一张，OEM 表 ID 叫 **`CPUSSDT`**，反编译后长这样：

```asl
Device (PLTF)
{
    Name (_HID, "ACPI0010")   // Processor Container Device
    Name (_CID, EisaId ("PNP0A05"))
    Device (C000) { Name (_HID, "ACPI0007") Name (_UID, Zero) }
    Device (C001) { Name (_HID, "ACPI0007") Name (_UID, One) }
    ... 一直到 C00F
}
```

### 3.2 这就是区别

| | 常见 B650（能装） | 这块 B850M |
|---|---|---|
| CPU 描述 | 传统 `Processor` 对象，放在 `\_PR` 下 | `ACPI0010` 容器 + `ACPI0007` 设备 |
| `_PR` 作用域 | 有 | **整个 DSDT 里一次都没出现** |
| 传统 `Processor` 对象（AML `0x5B83`） | 有 | **0 个** |

macOS 的 `AppleACPIPlatform` 是按**传统 `Processor` 对象**枚举 CPU 的。
你这块板用的是 ACPI 6.x 的「新式写法」——Windows 支持，macOS 不认识。

**这解释了为什么 `cpus=1` 会改变行为**：CPU 枚举路径本来就是歪的。

---

## 04. 第一次真正的突破：XOSI

继续翻 DSDT，发现 **29 处 `_OSI` 判断**，标准的「操作系统版本阶梯」：

```asl
If (_OSI ("Windows 2001")) { OSYS = 0x07D0 }
ElseIf (_OSI ("Windows 2001.1")) { ... }
...
ElseIf (_OSI ("Windows 2015")) { OSYS = 0x07DC }
```

macOS 只报 `_OSI("Darwin")`，所以这一整串 `If` **全部不匹配**，`OSYS` 停留在最低值。
固件于是走了「兼容/最老」的初始化分支——CPU 容器、PEP、PCIe 都可能没被正确初始化。

### 解法：骗固件说「我是 Windows」

1. 用 SSDT 定义 `XOSI` 方法：对 `Windows *` 一律返回真
2. 用 OpenCore 的 ACPI Patch 把 DSDT 里的 `_OSI` 全部改名成 `XOSI`

**效果立竿见影**：

```
改之前：进度条永远 0%
改之后：进度条走到 50%
```

这是整晚第一次看到这台机器「在加载 macOS」。

---

## 05. 50% 之后：APFS 与安装器的坑

进度条卡在 50% 很久。查资料发现 Tahoe 在 AMD 上需要 **`apfs_aligned.efi`**（APFS 对齐修复）。

但我们的 OpenCore 1.0.8 加载它时报：

```
OC: Driver apfs_aligned.efi at 4 cannot be loaded - Unsupported!
Halting on critical error
```

后来在 1401 那支盘上发现：**它的 OpenCore 更新（REL-107），能加载同一个驱动**。
把两支盘的长处拼起来：

- 1401 的新 OpenCore + 真 `apfs_aligned.efi`
- 加上我们验证过的 `XOSI`
- 去掉 NullMoth 的早期启动参数（`nvfb=1`、`amfi=0x80` 这些会让内核早期就卡住）

结果：**安装器完整启动**。

### 然后卡在 99%

安装器第二阶段要联网下载 12–15 GB。
这台机器的网络：

- `ping apple.com` 丢包 **33%**
- 系统时钟被重置（证书校验会失败）
- 于是下载中断、卡 99%，一等就是半小时

试了三次，总共耗掉三个小时。

---

## 06. 换思路：不要在物理机上装

> **如果安装器不靠谱，那就别用它装。**

手里有一台**已经装好、能进桌面**的虚拟机。
macOS 的系统盘和硬件没有绑定关系——决定能不能启动的是 EFI，不是硬盘里的系统。

于是：

```
虚拟机里装好的系统  ──克隆──▶  物理 SATA SSD  ──▶  真机启动
```

### 技术上怎么做的

1. **VMware 挂物理盘**：虚拟机设置 → 添加硬盘 → 使用物理磁盘 → PhysicalDrive0
   - 坑：手写 `.vmdk` 描述文件会被 VMware 静默忽略（`no device present`），**必须用图形向导**
   - 前提：目标盘在 Windows 里 `offline`
2. **恢复环境里做克隆**：磁盘工具 → 抹掉 SSD 为 APFS → 从 `Macintosh HD` **恢复**
   - 「验证来源」这步很慢（30–40 GB 要 10–20 分钟），属正常
3. **跳过设置向导**：克隆出来的系统会重新跑 Setup Assistant，卡在「文件加密」那一步。
   在恢复环境终端里补一个标记即可：

   ```bash
   sudo touch /Volumes/*/private/var/db/.AppleSetupDone
   ```

4. **真机启动**：F11 → OpenCore U 盘 → 选 SSD 上的系统 → **登录界面** → 桌面。

---

## 07. 回头看：哪些「常识」是错的

| 常识 | 实际 |
|---|---|
| 「B850 + 7800X3D 装不了 macOS」 | 能装，只是不能用常规方法 |
| 「卡 PCI 是显卡问题」 | 拔了显卡一样卡；是固件 ACPI/PCIe 初始化 |
| 「BIOS 越新越好」 | 换了一代 AGESA 也没用；但也不是 BIOS 的锅 |
| 「`-v` 只是多打印点日志」 | 它改变了启动时序，**直接触发 PCI 竞态**，不开能跑到 50%，开了就卡死 |
| 「必须用安装器装」 | 虚拟机克隆一条路，绕开所有网络和安装器问题 |

## 08. 最后

从晚上八点折腾到凌晨三点，中间无数次以为「这块板就是不行」。

真正让它跑起来的，不是什么高深技术，而是两个念头：

1. **「固件到底给系统描述了什么？」** —— 于是挖出了 ACPI0010
2. **「为什么一定要用安装器？」** —— 于是改成了克隆

以及一个很朴素的判断：

> 论坛上那个人失败了，不代表这件事不可能。
> 只代表**还没有人找到那条路**。

现在这条路写在这里了。下一个遇到同款主板的人，不用再熬一个通宵。
