# 可复现步骤：从零到桌面

> 目标：在 **AMD B850 + Zen4/Zen5 + NVIDIA Turing/Blackwell** 的机器上装 macOS 26 Tahoe。
> 全程**不需要**在物理机上跑联网安装器。

---

## 前置条件

| 项目 | 要求 |
|---|---|
| Windows 主机 | 能跑 VMware Workstation 17+ |
| 一块 SSD | 至少 100 GB，会被整盘抹掉 |
| 一个 U 盘 | ≥ 16 GB，做 OpenCore 引导盘 |
| macOS 虚拟机 | 能正常启动到桌面（本文用 OC4VM + Tahoe） |
| 时间 | 约 3–5 小时（大头是克隆和首次启动） |

---

## 第一部分：准备 EFI 引导盘

### 1.1 用 1401 生成基础 EFI（推荐）

[1401](https://github.com/) 会一键生成 OpenCore + 恢复镜像 + NullMoth 参数。

生成后，**只保留 EFI 部分**，后面手动改三处。

### 1.2 加入 XOSI（关键！）

1. 把 `assets/efi/SSDT-XOSI.aml` 放进 `EFI/OC/ACPI/`
2. 在 `config.plist` 的 `ACPI → Add` 里加一条：

   ```xml
   <dict>
     <key>Comment</key><string>XOSI: pretend Windows to firmware</string>
     <key>Enabled</key><true/>
     <key>Path</key><string>SSDT-XOSI.aml</string>
   </dict>
   ```

3. 在 `ACPI → Patch` 里加「`_OSI` → `XOSI`」重命名：

   ```xml
   <dict>
     <key>Comment</key><string>OSI to XOSI (DSDT)</string>
     <key>Enabled</key><true/>
     <key>Find</key><data>X09TSQ==</data>        <!-- "_OSI" -->
     <key>Replace</key><data>WE9TSQ==</data>     <!-- "XOSI" -->
     <key>TableSignature</key><data>RFNEVA==</data> <!-- "DSDT" -->
     <key>Count</key><integer>0</integer>
   </dict>
   ```

   > base64：`X09TSQ==` = `_OSI`，`WE9TSQ==` = `XOSI`，`RFNEVA==` = `DSDT`

### 1.3 确认 apfs_aligned 能加载

`EFI/OC/Drivers/apfs_aligned.efi` 必须存在，并在 `UEFI → Drivers` 注册。

⚠️ **OpenCore 版本要求**：1.0.7 及以上。
如果启动时看到：

```
OC: Driver apfs_aligned.efi ... cannot be loaded - Unsupported!
Halting on critical error
```

说明你的 OpenCore 太旧，换 1401 自带的那份 `OpenCore.efi` + `BOOTx64.efi`。

### 1.4 设置 boot-args

```
keepsyms=1 -no_compat_check npci=0x2000
```

**不要加 `-v`**（见排错手册第 1 条）。
**不要加** NullMoth 的早期参数（`nvfb=1` 等）——装机阶段用不上，还会让内核早期卡住。

### 1.5 SMBIOS

`PlatformInfo → Generic → SystemProductName` 必须是 **MacPro7,1**。
（`iMacPro1,1` 的 board-id `Mac-7BA5B2D9E42DDD94` 在 Tahoe 上会被拒绝。）

---

## 第二部分：确认虚拟机里的系统可用

1. 启动你的 macOS 虚拟机（VMware）
2. 能进桌面、能登录 → OK
3. 记下登录密码，后面真机要用

> 如果虚拟机也进不去，先修好它。克隆的前提是源系统可用。

---

## 第三部分：把物理 SSD 挂给虚拟机

### 3.1 Windows 里离线磁盘

管理员 PowerShell：

```powershell
diskpart
select disk N        # 确认是那块要装的 SSD！
offline disk
exit
```

### 3.2 VMware 图形界面添加

1. 虚拟机关机
2. **虚拟机 → 设置 → 添加 → 硬盘 → 下一步**
3. 类型 **SATA** → 下一步
4. 选 **「使用物理磁盘（仅供高级用户）」**
5. 设备选 **PhysicalDriveN**（对应那块 SSD）
6. 用途选 **「使用整个磁盘」** → 完成

⚠️ 不要手写 `.vmdk` 描述文件——VMware 会静默忽略，症状是恢复环境里看不到那块盘。

### 3.3 启动虚拟机，进恢复环境

OpenCore 菜单 → **macOS Base System**（或 `Recovery`）→ 磁盘工具。

---

## 第四部分：克隆

### 4.1 抹掉物理盘

磁盘工具 → 菜单 **显示 → 显示所有设备** → 选中那块 200+ GB 的物理盘 → **抹掉**：

- 名称：`MacSSD`
- 格式：**APFS**
- 方案：**GUID 分区图**

### 4.2 恢复

1. 左侧选中源卷 **`Macintosh HD`**（⚠️ 不要选 `Macintosh HD - 数据`）
2. 右上 **恢复**
3. 「恢复到」选 `MacSSD`
4. 开始

**「正在验证来源…」会持续 10–20 分钟**，进度条几乎不动是正常的（它在算校验和）。
之后进入复制阶段，再 20–40 分钟。

---

## 第五部分：跳过设置向导

克隆出来的系统在真机上第一次启动会跑 Setup Assistant，并可能卡在「文件加密」。

在恢复环境（物理机也行、虚拟机也行）的**终端**里执行：

```bash
sudo touch /Volumes/*/private/var/db/.AppleSetupDone
```

验证：

```bash
ls -la /Volumes/*/private/var/db/.AppleSetupDone
```

> 用通配符是因为卷名可能带中文（`Macintosh HD - 数据 1`），
> 而源系统卷是只读的，写它会报错——无害。

---

## 第六部分：真机启动

1. 关机，把 SSD 接回主板
2. BIOS：CSM 关、Secure Boot 关、Above 4G 开、ReBAR 关、核显关、XHCI Hand-off 开
3. 开机 **F11** → OpenCore U 盘
4. 菜单里选 **SSD 上的系统卷**
5. 首次启动会重建 kext 缓存，**2–5 分钟**，别急
6. 出现**登录界面** → 输入密码 → 桌面

---

## 第七部分：收尾

### 7.1 把 EFI 装到硬盘（脱离 U 盘）

1. 挂载 SSD 的 EFI 分区（`diskutil list` 找到 200 MB 那个，`diskutil mount diskXs1`）
2. 把 U 盘里的 `EFI` 文件夹整个复制进去
3. BIOS 启动顺序里把「UEFI: SSD」调到第一位

### 7.2 装 NullMoth（N 卡加速）

U 盘根目录 `NullMoth/nvidia-2.7.2.tar.gz`：

```bash
tar -xzf nullmoth-nvidia-2.7.2.tar.gz
cd pkgroot
sudo ./install.sh
sudo shutdown -r now
```

### 7.3 检查清单

- [ ] 网络（`RTL812xLucy.kext` 应自动驱动 RTL8126）
- [ ] 声音（AppleALC + `alcid` 布局 ID）
- [ ] USB 端口映射（USBToolBox + UTBDefault）
- [ ] 睡眠/唤醒
- [ ] 显卡 Metal 加速（NullMoth 生效后 `system_profiler SPDisplaysDataType` 应显示 Metal 支持）

---

## 最小可用文件清单

```
EFI/OC/
├── config.plist              ← 见 assets/efi/config.plist（需替换序列号）
├── ACPI/
│   ├── SSDT-XOSI.aml         ← 关键
│   └── SSDT-PLUG-ALT.aml
├── Drivers/
│   └── apfs_aligned.efi      ← 关键，需 OpenCore ≥ 1.0.7
└── Kexts/
    ├── Lilu.kext
    ├── VirtualSMC.kext
    ├── WhateverGreen.kext
    ├── AppleALC.kext
    ├── RTL812xLucy.kext
    ├── USBToolBox.kext + UTBDefault.kext
    ├── NVMeFix.kext
    └── RestrictEvents.kext
```
