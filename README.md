# 鍦ㄤ竴鍙般€岀湅璧锋潵涓嶅彲鑳姐€嶇殑 B850 涓绘澘涓婅 macOS Tahoe 26

> 7800X3D + 涓冨僵铏?B850M-PLUS S WIFI7 + RTX 5070 Ti
> 浠庛€屽崱 PCI 鏃犺В銆嶅埌銆岃繘妗岄潰銆嶏紝涓€涓€氬鐨勫叏閮ㄨ褰曘€?
---

## 涓€鍙ヨ瘽缁撹

**杩欏潡鏉胯兘璺?macOS銆?* 浣嗗畠涓嶆槸闈?瑁?涓婂幓鐨勶紝鏄潬**缁?*涓婂幓鐨勶細

> 涓嶈鍜屽畨瑁呭櫒姝荤 鈥斺€?鍦ㄨ櫄鎷熸満閲岃濂斤紝鍐嶆妸绯荤粺**鍏嬮殕**鍒扮墿鐞嗙‖鐩樸€?
---

## 纭欢

| 閮ㄤ欢 | 鍨嬪彿 | 澶囨敞 |
|---|---|---|
| CPU | AMD Ryzen 7 7800X3D | 8C/16T锛孉M5 |
| 涓绘澘 | 涓冨僵铏?BATTLE-AX B850M-PLUS S WIFI7 V14 | BIOS 1004 鈫?1010 |
| 鍐呭瓨 | 32 GB DDR5-6000 | EXPO |
| 鏄惧崱 | NVIDIA RTX 5070 Ti 16GB | 闇€ NullMoth 椹卞姩 |
| 缃戝崱 | Realtek RTL8126 5GbE | EFI 閲?`RTL812xLucy.kext` 鏀寔 |
| 鏃犵嚎 | MediaTek RZ717 WiFi 7 | macOS 鏃犻┍鍔?|
| 澹板崱 | Realtek ALC897 | AppleALC |

## 鏈€缁堣兘鐢ㄧ殑鏂规锛圱L;DR锛?
```
鈶?铏氭嫙鏈猴紙VMware + OC4VM锛夐噷瑁呭ソ macOS 26 Tahoe
        鈫?鈶?鐢?VMware銆岀墿鐞嗙鐩樼洿閫氥€嶆妸 SATA SSD 鎸傜粰铏氭嫙鏈?        鈫?鈶?鎭㈠鐜 鈫?纾佺洏宸ュ叿 鈫?鎶?Macintosh HD 鎭㈠鍒?SSD
        鈫?鈶?鎭㈠鐜缁堢 鈫?touch /Volumes/*/private/var/db/.AppleSetupDone
        鈫?鈶?鐗╃悊鏈?F11 鈫?OpenCore U 鐩?鈫?閫?SSD 涓婄殑绯荤粺 鈫?杩涙闈?```

寮曞鐢ㄧ殑 EFI 鍏抽敭鐐癸細

- **OpenCore 1.0.7+**锛?401 v2.7.2 鑷甫锛岃兘鍔犺浇 `apfs_aligned.efi`锛?- **SSDT-XOSI + `_OSI`鈫抈XOSI` 閲嶅懡鍚嶈ˉ涓?*锛堣鍥轰欢璧?Windows 鍒濆鍖栬矾寰勶級
- `SSDT-PLUG-ALT`锛圓CPI0010 瀹瑰櫒鐨?CPU 鎻掍欢锛?- boot-args锛歚keepsyms=1 -no_compat_check npci=0x2000`

## 涓轰粈涔堝€煎緱鍐欎笅鏉?
璁哄潧涓婃悳鍒拌繃鍚屾 B850 + 9950X3D 鍗″湪鍚屼竴澶勭殑甯栧瓙锛屾渶鍚庢病鏈夌粨璁恒€?鎴戞妸杩欐潯**缁曡繃鍘?*鐨勮矾瀹屾暣璁板綍涓嬫潵 鈥斺€?鍖呮嫭鎵€鏈夊け璐ョ殑灏濊瘯锛屽洜涓洪偅浜涘け璐ユ湰韬氨鏄俊鎭€?
## 鐩綍

| 鏂囦欢 | 鍐呭 |
|---|---|
| [docs/01-鎺㈢储绾疄.md](docs/01-鎺㈢储绾疄.md) | 閫氬鐨勫叏杩囩▼锛氭瘡涓€姝ヨ瘯浜嗕粈涔堛€佷负浠€涔堝け璐?|
| [docs/02-鍙鐜版楠?md](docs/02-鍙鐜版楠?md) | 浠庨浂鍒版闈㈢殑瀹屾暣鎿嶄綔鎵嬪唽 |
| [docs/03-鎺掗敊鎵嬪唽.md](docs/03-鎺掗敊鎵嬪唽.md) | 鐥囩姸 鈫?鍘熷洜 鈫?瑙ｆ硶瀵圭収琛?|
| [docs/04-鑷村悓璺汉.md](docs/04-鑷村悓璺汉.md) | 缁欒鍧涗笂閭ｄ綅鍗′綇鐨勬湅鍙嬬殑鍥炰俊 |

## 绱犳潗

- `assets/efi/` 鈥斺€?鏈€缁堝彲鐢ㄧ殑 `config.plist`锛堝凡鑴辨晱锛夈€乣SSDT-XOSI`銆乣SSDT-PLUG-ALT`
- `assets/evidence/` 鈥斺€?璇佹槑杩欏潡鏉跨敤 ACPI0010 瀹瑰櫒鐨?CPUSSDT 鍙嶇紪璇?- `assets/scripts/` 鈥斺€?鏈鐢ㄥ埌鐨勫皬宸ュ叿锛堢敓鎴?XOSI銆佽В鏋?MADT銆佹寕鐗╃悊鐩樼瓑锛?
## 璁稿彲

- 鏂囨。锛欳C BY-SA 4.0
- 鑴氭湰锛歁IT

## 鑷磋阿

- [OpenCore](https://github.com/acidanthera/OpenCorePkg) / [Lilu](https://github.com/acidanthera/Lilu) / [VirtualSMC](https://github.com/acidanthera/VirtualSMC) 绛?Acidanthera 椤圭洰
- [1401](https://github.com/)锛圢ullMoth 涓€閿伐鍏凤級涓?NullMoth 椹卞姩
- [RapidEFI-Tool](https://github.com/JeoJay127/RapidEFI-Tool)锛坄apfs_aligned.efi` 鏉ユ簮锛?- [OC4VM](https://github.com/DrDonk)锛堣櫄鎷熸満妯℃澘锛?- 浠ュ強鎵€鏈夋妸缁忛獙鏃犲伩鍐欏湪璁哄潧閲岀殑闄岀敓浜?鈥斺€?杩欑瘒鏂囩珷涔熸槸杩樼粰浠栦滑鐨勩€?
