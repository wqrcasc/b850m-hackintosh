import os, shutil, plistlib, subprocess, time

print('1) stop 1401')
subprocess.run(['taskkill', '/PID', '18500', '/F'], capture_output=True)

time.sleep(2)
print('2) format H: FAT32')
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Format-Volume -DriveLetter H -FileSystem FAT32 -NewFileSystemLabel '1401' -Confirm:$false | Out-Null; 'ok'"],
                   capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[:300])

print('3) copy EFI')
src_efi = r'D:\桌面\折腾\12_macOS\EFI_build'
dst_efi = r'H:\EFI'
if os.path.exists(dst_efi):
    shutil.rmtree(dst_efi)
shutil.copytree(src_efi, dst_efi)
print('   files:', sum(len(f) for _, _, f in os.walk(dst_efi)))

print('4) copy recovery image')
rec = r'H:\com.apple.recovery.boot'
os.makedirs(rec, exist_ok=True)
shutil.copy2(r'D:\桌面\折腾\macos-vm\oc4vm\tools\windows\tahoe.dmg', os.path.join(rec, 'BaseSystem.dmg'))
shutil.copy2(r'D:\桌面\折腾\macos-vm\oc4vm\tools\windows\tahoe.chunklist', os.path.join(rec, 'BaseSystem.chunklist'))

print('5) patch boot-args add cpus=1')
cfg = r'H:\EFI\OC\config.plist'
d = plistlib.load(open(cfg, 'rb'))
nv = d['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']
old = nv.get('boot-args', '')
if 'cpus=1' not in old:
    nv['boot-args'] = (old + ' cpus=1').strip()
d['NVRAM']['Delete']['7C436110-AB2A-4BBB-A880-FE41995C9F82'] = ['boot-args']
plistlib.dump(d, open(cfg, 'wb'))
print('   old:', old)
print('   new:', nv['boot-args'])

print('6) verify')
for p in [r'H:\EFI\BOOT\BOOTx64.efi', r'H:\EFI\OC\config.plist',
          r'H:\com.apple.recovery.boot\BaseSystem.dmg',
          r'H:\com.apple.recovery.boot\BaseSystem.chunklist']:
    print('  ', p, os.path.getsize(p) if os.path.exists(p) else 'MISSING')
