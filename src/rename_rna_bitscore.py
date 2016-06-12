from os.path import join, basename, dirname, exists
from os import makedirs

# file = '../queries/fam40_typedistributed_plain_bg/fam40_typedistributed_plain_bg.bitscore'
query = 'fam40_typedistributed_bg'
file = join('../queries', query, query + '.bitscore')

output = []
with open(file, 'r') as handle:
    output.append(handle.readline().strip())
    for line in handle:
        line = line.strip()
        output.append(line.replace('RF', 'QRF'))

outdir = dirname(file) + '-rename'
if not exists(outdir):
    makedirs(outdir)
outfile = join(outdir, ''.join(basename(file).split('.')[:-1]) + '-rename.bitscore')
print('outfile:', outfile)
with open(outfile, 'w') as handle:
    for line in output:
        handle.write(line + '\n')