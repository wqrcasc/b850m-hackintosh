import re, os, subprocess

dsl = open(r'C:\dshtmp\acpi\DSDT.dsl', encoding='utf-8', errors='ignore').read()
strings = sorted(set(re.findall(r'_OSI\s*\(\s*"([^"]+)"', dsl)))
print('OSI strings:', strings)

windows = [s for s in strings if s.startswith('Windows') and 'NT' not in s]
others = [s for s in strings if s not in windows]
print('windows:', windows)
print('others:', others)

lines = []
lines.append('DefinitionBlock ("", "SSDT", 2, "OC", "XOSI", 0x00000001)')
lines.append('{')
lines.append('    Method (XOSI, 1, NotSerialized)')
lines.append('    {')
for i, s in enumerate(windows):
    kw = 'If' if i == 0 else 'ElseIf'
    lines.append(f'        {kw} (Arg0 == "{s}")')
    lines.append('        {')
    lines.append('            Return (One)')
    lines.append('        }')
lines.append('        Return (Zero)')
lines.append('    }')
lines.append('}')
src = '\n'.join(lines) + '\n'
os.makedirs(r'C:\dshtmp\xosi', exist_ok=True)
p = r'C:\dshtmp\xosi\SSDT-XOSI.dsl'
open(p, 'w', encoding='utf-8').write(src)
print(src[:600])

r = subprocess.run(['iasl', '-p', r'C:\dshtmp\xosi\SSDT-XOSI.aml', p], capture_output=True, text=True)
print((r.stdout or '')[-500:])
print('aml:', os.path.exists(r'C:\dshtmp\xosi\SSDT-XOSI.aml'),
      os.path.getsize(r'C:\dshtmp\xosi\SSDT-XOSI.aml') if os.path.exists(r'C:\dshtmp\xosi\SSDT-XOSI.aml') else 0)
