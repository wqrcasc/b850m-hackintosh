import plistlib

cfg = r'H:\EFI\OC\config.plist'
d = plistlib.load(open(cfg, 'rb'))

g = d['PlatformInfo']['Generic']
print('before:', {k: g.get(k) for k in ('SystemProductName', 'SystemSerialNumber', 'MLB', 'SystemUUID', 'ROM')})

g['SystemProductName'] = 'MacPro7,1'
g['SystemSerialNumber'] = 'F5KKQ1YKP7QM'
g['MLB'] = 'F5K320306QXK3F7FB'
g['SystemUUID'] = '7BD810D2-A82C-4860-BF85-A22B214297CD'
g['ROM'] = bytes([0x4d, 0x68, 0x08, 0x0e, 0x12, 0xe1])

nv = d['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']
old = nv.get('boot-args', '')
if '-no_compat_check' not in old:
    nv['boot-args'] = (old + ' -no_compat_check').strip()
d['NVRAM']['Delete']['7C436110-AB2A-4BBB-A880-FE41995C9F82'] = ['boot-args']

plistlib.dump(d, open(cfg, 'wb'))
print('after :', {k: g.get(k) for k in ('SystemProductName', 'SystemSerialNumber', 'MLB', 'SystemUUID', 'ROM')})
print('boot-args:', nv['boot-args'])
