import os, shutil, subprocess, re

VM = r'D:\桌面\折腾\macos-vm\OC4VM-Tahoe'
vmx = os.path.join(VM, 'macos.vmx')

# 1) offline disk 0
dp = subprocess.run(['diskpart'], input='select disk 0\noffline disk\nexit\n', capture_output=True, text=True)
print('offline:', 'successfully' in dp.stdout.lower() or '成功' in dp.stdout)

# 2) descriptor
sectors = 500118192
desc = f'''# Disk DescriptorFile
version=1
encoding="UTF-8"
CID=fffffffe
parentCID=ffffffff
createType="fullDevice"

# Extent description
RW {sectors} FLAT "\\\\.\\PhysicalDrive0" 0

# The Disk Data Base
#DDB
ddb.adapterType = "sata"
ddb.geometry.cylinders = "31098"
ddb.geometry.heads = "255"
ddb.geometry.sectors = "63"
ddb.virtualHWVersion = "21"
'''
open(os.path.join(VM, 'physical0.vmdk'), 'w', encoding='ascii').write(desc)
print('descriptor written')

# 3) vmx: only add sata0:3, leave cdrom untouched
shutil.copy2(vmx, vmx + '.bak2')
txt = open(vmx, encoding='utf-8', errors='ignore').read()
if 'sata0:3.present' in txt:
    print('sata0:3 already present')
else:
    txt = txt.rstrip() + '\nsata0:3.present = "TRUE"\nsata0:3.fileName = "physical0.vmdk"\nsata0:3.deviceType = "disk"\n'
    open(vmx, 'w', encoding='utf-8').write(txt)
    print('sata0:3 added')

for line in open(vmx, encoding='utf-8', errors='ignore').read().splitlines():
    if re.match(r'(sata|scsi|nvme|ide)\d', line):
        print(' ', line)
