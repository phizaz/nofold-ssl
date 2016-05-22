import os
from Bio import SeqIO

file = 'Rfam-seed/rfam75id_rename/rfam75id.db'

with open(file, 'r') as handle:
    records = list(SeqIO.parse(handle, 'fasta'))
    for record in records:
        record.id = record.name = str(record.id).replace('RF', 'QRF')
        record.description = ''

with open(file, 'w') as handle:
    print(records)
    SeqIO.write(records, handle, 'fasta')