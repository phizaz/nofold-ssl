from os.path import join, basename, dirname, exists
from os import makedirs
from argparse import ArgumentParser

raise NotImplemented # need refactoring

parser = ArgumentParser(description='rename rna bitscore')
parser.add_argument('--query', action='store', required=True)
args = parser.parse_args()

query = args.query
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