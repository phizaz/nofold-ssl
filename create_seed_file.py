import os, sys
from os.path import isfile, join
from Bio import SeqIO
from multiprocessing.dummy import Pool as ThreadPool

root = 'Rfam-seed/fasta'

files = [f for f in os.listdir(root) if isfile(join(root, f)) and f != '.DS_Store']

def get_records(file):
    family = file.split('.')[0]
    path = join(root, file)
    print(path)
    with open(path) as file:
        records = SeqIO.parse(file, 'fasta')
        results = []
        for record in records:
            short, excess = record.name.split('/')
            new_name = family + '_' + short
            # alter the record by adding family in front
            record.id = new_name
            record.name = new_name
            record.description = ''
            results.append(record)
        return results

POOL_SIZE = len(files)
pool = ThreadPool(processes=POOL_SIZE)

output = pool.map(get_records, files)
records = [record for each in output for record in each]

with open('Rfam-seed/Rfam-seed.db', 'w') as file:
    SeqIO.write(records, file, 'fasta')
