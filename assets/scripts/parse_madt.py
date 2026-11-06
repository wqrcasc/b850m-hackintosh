import glob

path = glob.glob(r'C:\dshtmp\acpi\*APIC*.aml')[0]
d = open(path, 'rb').read()
print('file', path, 'len', len(d))
i = 36
cpus = []
while i + 2 <= len(d):
    t = d[i]
    l = d[i + 1]
    if l == 0:
        break
    if t == 0 and l >= 8:
        cpus.append((d[i + 2], d[i + 3], d[i + 4]))
    i += l
print('cpu entries', len(cpus))
for c in cpus:
    print('  acpi_id=%d apic_id=%d flags=0x%02X' % c)
