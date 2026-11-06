# 致同路人：给论坛上那位卡住的朋友

> 这不是技术文档，是一封回信。
> 写给所有在 `CoreAnalyticsHub start completed` 那一行前面坐过一整晚的人。

---

## 中文版

兄弟：

我看到你的帖子了。B850 + 9950X3D，卡在 `AMDCPUSupport::start trying to init PCI service`，
USB 一起掉，换了几版 BIOS 也没用，最后那个帖子沉了。

我想告诉你：**你没有做错什么，也不是这块板「不能装」。**

我用的是一块七彩虹 B850M-PLUS S WIFI7，症状和你一模一样：

- 内核能起来，停在 `CoreAnalyticsHub start completed`
- 同一瞬间 USB 全部失效
- 没有 panic，没有任何提示，就是不动
- 拔掉显卡、换 OpenCore、换 macOS 版本，全都没用

我熬了一个通宵，最后找出了两条关键线索，都写在仓库里了：

**第一，这块板的 CPU 不是传统写法。**
它的 DSDT 里 `_PR` 一次都没出现，CPU 是 `ACPI0010` 容器 + `ACPI0007` 设备，定义在一张叫 `CPUSSDT` 的 SSDT 里。
macOS 的 `AppleACPIPlatform` 按传统 `Processor` 对象找 CPU，找不到，后面的 PCI/中断初始化就走歪了。

**第二，固件在等一句 `_OSI("Windows ...")`。**
DSDT 里有 29 处 `_OSI` 判断，macOS 只报 `Darwin`，全部不匹配，`OSYS` 停在最低值，固件于是走「最老兼容」分支。

把 `_OSI` 改名成 `XOSI`、再用 SSDT 让固件以为自己是 Windows 之后——
**进度条第一次动了，从 0% 走到了 50%。**

但真正让我进桌面的，是第三个想法：

> **为什么一定要用安装器装？**

我在虚拟机里装好了同一个系统，然后把整卷**克隆**到物理 SSD 上——
不联网、不下载、不碰安装器的 99%。

现在这台机器已经在跑 macOS 26 Tahoe 了。

## 所以，如果你还想试

仓库里有：

- 完整的操作步骤（`docs/02-可复现步骤.md`）
- 每一步失败的记录和原因（`docs/01-探索纪实.md`、`docs/03-排错手册.md`）
- 可以直接用的 `SSDT-XOSI`、`config.plist`（记得换成你自己的序列号）

不用谢，也不用署名。**我写下来，就是因为当年搜你的帖子时，多希望有人写过。**

如果你试成了，也请把你的板子型号和结果发出来——
下一个搜到这条帖子的人，会感谢你。

—— 一个同样在这行字前面坐了一晚上的人

---

## English version

Hey man,

I saw your thread. B850 + 9950X3D, stuck at `AMDCPUSupport::start trying to init PCI service`,
USB dying at the same moment, several BIOS versions tried, thread went cold.

I want to tell you: **you didn't do anything wrong, and it's not that the board "can't run macOS".**

I hit the exact same wall on a Colorful B850M-PLUS S WIFI7:

- kernel starts, stops right after `CoreAnalyticsHub start completed`
- USB dies at the same instant
- no panic, no error, just silence
- removing the GPU, swapping OpenCore, switching macOS versions — nothing helped

I spent a whole night on it and found two things, both written up in the repo:

**1. This board doesn't describe CPUs the classic way.**
There is no `_PR` scope in its DSDT at all. CPUs are an `ACPI0010` processor container
with `ACPI0007` devices, defined in an SSDT with OEM ID `CPUSSDT`.
`AppleACPIPlatform` looks for legacy `Processor` objects, doesn't find them,
and the subsequent PCI/interrupt bring-up goes sideways.

**2. The firmware is waiting for an `_OSI("Windows ...")` answer.**
The DSDT has 29 `_OSI` checks that set `OSYS`. macOS only answers `Darwin`,
so every check fails, `OSYS` stays at the lowest value, and the firmware
takes its "oldest compatible" init path.

After renaming `_OSI` to `XOSI` and letting an SSDT answer "yes, I'm Windows",
**the progress bar moved for the first time — from 0% to 50%.**

But what actually got me to the desktop was a third thought:

> **Why insist on using the installer at all?**

I installed the same system inside a VM, then **cloned the whole volume** onto a physical SSD.
No network, no 13 GB download, no 99% hang.

That machine is running macOS 26 Tahoe now.

## If you still want to try

The repo has:

- a complete step-by-step guide (`docs/02-可复现步骤.md`)
- the full failure log and reasoning (`docs/01-探索纪实.md`, `docs/03-排错手册.md`)
- ready-to-use `SSDT-XOSI` and `config.plist` (swap in your own serials)

No credit needed. **I wrote it down because, while reading your thread, I desperately wished someone had.**

If you get it working, please post your board model and result.
The next person who finds your thread will thank you.

— someone who also sat in front of that same line all night
