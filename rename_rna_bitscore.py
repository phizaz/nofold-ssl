file = 'Rfam-seed/rfam75id_rename/rfam75id.bitscore'

output = []

with open(file, 'r') as handle:
    output.append(handle.readline().strip())
    for line in handle:
        line = line.strip()
        output.append(line.replace('RF', 'QRF'))

with open(file, 'w') as handle:
    for line in output:
        handle.write(line + '\n')