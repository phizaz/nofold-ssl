from os.path import join, basename, dirname, exists
from os import makedirs
from Bio import SeqIO

# file = '../queries/fam40_typedistributed_plain_bg/fam40_typedistributed_plain_bg.db'
query = 'fam40_typedistributed_bg'
file = join('../queries', query, query + '.db')

with open(file, 'r') as handle:
    records = list(SeqIO.parse(handle, 'fasta'))
    for record in records:
        record.id = record.name = str(record.id).replace('RF', 'QRF')
        record.description = ''

outdir = dirname(file) + '-rename'
if not exists(outdir):
    makedirs(outdir)
outfile = join(outdir, ''.join(basename(file).split('.')[:-1]) + '-rename.db')
print('outfile:', outfile)
with open(outfile, 'w') as handle:
    print(records)
    SeqIO.write(records, handle, 'fasta')