# 在一台「看起来不可能」的 B850 主板上装 macOS Tahoe 26

> 7800X3D + 七彩虹 B850M-PLUS S WIFI7 + RTX 5070 Ti
> 从「卡 PCI 无解」到「进桌面」，一个通宵的全部记录。

---

## 一句话结论

**这块板能跑 macOS。** 但它不是靠"装"上去的，是靠**绕**上去的：

> 不要和安装器死磕 —— 在虚拟机里装好，再把系统**克隆**到物理硬盘。

---

## 硬件

| 部件 | 型号 | 备注 |
|---|---|---|
| CPU | AMD Ryzen 7 7800X3D | 8C/16T，AM5 |
| 主板 | 七彩虹 BATTLE-AX B850M-PLUS S WIFI7 V14 | BIOS 1004 → 1010 |
| 内存 | 32 GB DDR5-6000 | EXPO |
| 显卡 | NVIDIA RTX 5070 Ti 16GB | 需 NullMoth 驱动 |
| 网卡 | Realtek RTL8126 5GbE | EFI 里 `RTL812xLucy.kext` 支持 |
| 无线 | MediaTek RZ717 WiFi 7 | macOS 无驱动 |
| 声卡 | Realtek ALC897 | AppleALC |

## 最终能用的方案（TL;DR）

```
① 虚拟机（VMware + OC4VM）里装好 macOS 26 Tahoe
        ↓
② 用 VMware「物理磁盘直通」把 SATA SSD 挂给虚拟机
        ↓
③ 恢复环境 → 磁盘工具 → 把 Macintosh HD 恢复到 SSD
        ↓
④ 恢复环境终端 → touch /Volumes/*/private/var/db/.AppleSetupDone
        ↓
⑤ 物理机 F11 → OpenCore U 盘 → 选 SSD 上的系统 → 进桌面
```

引导用的 EFI 关键点：

- **OpenCore 1.0.7+**（1401 v2.7.2 自带，能加载 `apfs_aligned.efi`）
- **SSDT-XOSI + `_OSI`→`XOSI` 重命名补丁**（让固件走 Windows 初始化路径）
- `SSDT-PLUG-ALT`（ACPI0010 容器的 CPU 插件）
- boot-args：`keepsyms=1 -no_compat_check npci=0x2000`

## 为什么值得写下来

论坛上搜到过同款 B850 + 9950X3D 卡在同一处的帖子，最后没有结论。
我把这条**绕过去**的路完整记录下来 —— 包括所有失败的尝试，因为那些失败本身就是信息。

## 目录

| 文件 | 内容 |
|---|---|
| [docs/01-探索纪实.md](docs/01-探索纪实.md) | 通宵的全过程：每一步试了什么、为什么失败 |
| [docs/02-可复现步骤.md](docs/02-可复现步骤.md) | 从零到桌面的完整操作手册 |
| [docs/03-排错手册.md](docs/03-排错手册.md) | 症状 → 原因 → 解法对照表 |
| [docs/04-致同路人.md](docs/04-致同路人.md) | 给论坛上那位卡住的朋友的回信 |

## 素材

- `assets/efi/` —— 最终可用的 `config.plist`（已脱敏）、`SSDT-XOSI`、`SSDT-PLUG-ALT`
- `assets/evidence/` —— 证明这块板用 ACPI0010 容器的 CPUSSDT 反编译
- `assets/scripts/` —— 本次用到的小工具（生成 XOSI、解析 MADT、挂物理盘等）

## 许可

- 文档：CC BY-SA 4.0
- 脚本：MIT

## 致谢

- [OpenCore](https://github.com/acidanthera/OpenCorePkg) / [Lilu](https://github.com/acidanthera/Lilu) / [VirtualSMC](https://github.com/acidanthera/VirtualSMC) 等 Acidanthera 项目
- [1401](https://github.com/)（NullMoth 一键工具）与 NullMoth 驱动
- [RapidEFI-Tool](https://github.com/JeoJay127/RapidEFI-Tool)（`apfs_aligned.efi` 来源）
- [OC4VM](https://github.com/DrDonk)（虚拟机模板）
- 以及所有把经验无偿写在论坛里的陌生人 —— 这篇文章也是还给他们的。
