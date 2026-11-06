# 排错手册：症状 → 原因 → 解法

> 全部来自这次实战，按出现顺序排列。每一条都对应真实日志或屏幕现象。

---

## 1. `-v` 一开就卡 PCI，不开能跑到 50%

**症状**

- 加 `-v`：停在 `CoreAnalyticsHub start completed`，USB 同时失效
- 不加 `-v`：进度条能走到 50%

**原因**

不是日志的问题，是**时序**。
`-v` 让内核打印变慢，刚好撞进固件 PCIe/ACPI 初始化的一个竞态窗口。
更快的启动能绕过它。

**解法**

- 装机阶段**不要加 `-v`**
- 需要看日志时，用「改一个变量、看进度条位置」的方式二分，而不是开 verbose

> 这是这次最反直觉的发现之一：**调试手段本身会改变被调试的行为。**

---

## 2. `STOP 0x11` + `This version of Mac OS X is not supported on this platform! Reason: Mac-7BA5B2D9E42DDD94`

**原因**

`Mac-7BA5B2D9E42DDD94` 是 **iMacPro1,1** 的 board-id。
**macOS 26 Tahoe 已经不支持 iMac Pro 2017。**

**解法**

- SMBIOS 改成 **MacPro7,1**
- 同时加 `-no_compat_check` 兜底

---

## 3. `STOP 0x16`（内核内存分配失败）

**原因**

`DevirtualiseMmio` 关着，固件留给 PCIe 的 MMIO 段（`0xE0000000`、`0xF7000000`、`0x860000000`）还占着内存映射，
内核找不到足够的连续低地址内存。

**解法**

`Booter → Quirks → DevirtualiseMmio = true`

---

## 4. 进度条 0%，卡 `CoreAnalyticsHub start completed`

**原因（本机真实原因）**

主板的 DSDT 里 **CPU 不是传统 `Processor` 对象**，而是：

```
ACPI0010（处理器容器）+ ACPI0007（处理器设备），挂在 \_SB.PLTF 下
```

macOS 的 `AppleACPIPlatform` 按传统写法找 CPU，找不到 → 后续 PCI/中断初始化走歪。

**验证方法**

```bash
# 反编译 DSDT，看有没有 _PR 和 Processor
iasl -d DSDT.aml
grep -c "_PR_" DSDT.dsl          # 0
grep -c "Processor (" DSDT.dsl   # 0
```

或者找 OEM 表 ID 为 `CPUSSDT` 的那张 SSDT（Windows 的枚举 API 可能看不到它，用 `acpidump` 能多 dump 出来）。

**解法**

`_OSI` → `XOSI` 重命名 + SSDT-XOSI（见下一条），**不要**自己造 `Processor` 对象
（实测会从「卡住」变成「panic」或「卡 0%」）。

---

## 5. 加 XOSI 后进度条从 0% 到 50%

**原理**

DSDT 里有 29 处 `_OSI("Windows ...")` 判断，用来设置 `OSYS` 变量。
macOS 只报 `_OSI("Darwin")`，所有判断都不匹配，`OSYS` 停最低值 →
固件走「兼容/最老」初始化路径。

**解法**

1. SSDT 定义 `XOSI`：对 `Windows *` 返回真
2. ACPI Patch 把 DSDT 的 `_OSI` 改名 `XOSI`

见 `assets/efi/SSDT-XOSI.dsl` 和 [02-可复现步骤.md](02-可复现步骤.md) 的 1.2 节。

---

## 6. `OC: Driver apfs_aligned.efi at 4 cannot be loaded - Unsupported!` + `Halting on critical error`

**原因**

OpenCore 版本太旧（1.0.8），加载不了这个驱动。

**解法**

换 1401 自带的新版 `OpenCore.efi`（REL-107 及以上）+ 对应的 `BOOTx64.efi`。

> `Halting on critical error` 是 OpenCore 的 `HaltLevel` 触发的：
> 任何 `DEBUG_ERROR` 都会让它直接停机。所以看到这句，先看**前一行**是什么错误。

---

## 7. 安装器卡 99%，一等半小时

**原因**

第二阶段要联网下载 12–15 GB。两个坑叠加：

1. **系统时钟不对** → HTTPS 证书校验失败
2. **网络丢包严重**（本机 `ping apple.com` 丢包 33%）

**解法（按性价比）**

- 先在恢复环境终端里修时间：

  ```bash
  date -u 110616522026      # 格式：月日时分年（UTC）
  ```

- 网络换 iPhone USB 共享（macOS 原生支持，免驱）
- **或者干脆放弃联网安装，改用虚拟机克隆**（见 [02](02-可复现步骤.md)）

---

## 8. 虚拟机挂物理盘：恢复环境里看不到那块盘

**症状**

VMware 日志里：

```
AHCI-VMM: sata0:3: Write to PxSCTL.DET while no device present
AHCI-VMM: sata0:3: Moved to Phys Offline state
```

**原因**

手写的 `.vmdk` 描述文件（`createType="fullDevice"`）被 VMware 静默忽略。
另外 Windows 里磁盘必须 **offline**。

**解法**

- 用 VMware **图形向导**添加（虚拟机 → 设置 → 添加 → 硬盘 → 使用物理磁盘）
- 它会自己生成正确的映射文件（如 `macos-1.vmdk`）和 `deviceType = "rawDisk"`

---

## 9. 恢复时「正在验证来源…」很久不动

**原因**

不是卡死，是在给 30–40 GB 数据算校验和。CPU 会持续跑满一个核。

**判断**

任务管理器里 `vmware-vmx` 的 CPU 时间持续增长 = 在干活。

**解法**

- 等 10–20 分钟
- 或者改用 `asr --noverify` 跳过校验

---

## 10. 克隆后的系统启动卡在「文件加密」设置页，鼠标能动但界面死

**原因**

克隆出来的系统会重新跑 Setup Assistant。FileVault 那一步在有/无 T2 的 hackintosh 上都可能挂。

**解法**

在恢复环境终端里写标记，完全跳过设置向导：

```bash
sudo touch /Volumes/*/private/var/db/.AppleSetupDone
```

（通配符避免中文卷名；源卷只读会报错，无害。）

---

## 11. 开机直接进 Windows，不进 macOS

**原因**

BIOS 启动顺序第一位是 Windows Boot Manager；OpenCore 在 U 盘上。

**解法**

- 每次开机按 **F11** 选 U 盘
- 或者把 EFI 复制到 SSD 的 EFI 分区后，把「UEFI: SSD」设为第一启动项

---

## 12. 一张速查表

| 症状 | 最可能原因 | 解法 |
|---|---|---|
| `STOP 0x11` + board-id | SMBIOS 机型太老 | 改 MacPro7,1 + `-no_compat_check` |
| `STOP 0x16` | MMIO 占内存 | `DevirtualiseMmio=true` |
| 卡 `CoreAnalyticsHub` | ACPI0010 CPU 描述 | SSDT-XOSI + `_OSI`→`XOSI` |
| 进度条 0% | 同上 | 同上 |
| 进度条 50% 不动 | APFS 挂载 | `apfs_aligned.efi`（OC ≥1.0.7） |
| `cannot be loaded - Unsupported` | OpenCore 太旧 | 换新版 OpenCore |
| 安装器 99% | 时钟/网络 | 修时间、换网络、或改用克隆 |
| 物理盘在虚拟机里不可见 | 手写 vmdk / 未 offline | 用图形向导 + `offline disk` |
| 设置向导卡「文件加密」 | Setup Assistant | `touch .AppleSetupDone` |
| `-v` 就卡死 | 时序竞态 | 别开 `-v` |
