import os, sys
from os.path import isfile, join
from Bio import SeqIO
from multiprocessing.dummy import Pool as ThreadPool

root = '../Rfam-seed/fasta'

files = [f for f in os.listdir(root) if isfile(join(root, f)) and f != '.DS_Store']

def worker(file):
    family = file.split('.')[0]
    path = join(root, file)
    print(path)

    alt_records = []
    with open(path) as file:
        records = SeqIO.parse(file, 'fasta')
        for record in records:
            short, excess = record.name.split('/')
            new_name = family + '_' + short
            # alter the record by adding family in front
            record.id = new_name
            record.name = new_name
            record.description = ''
            alt_records.append(record)

    output_db = join('../Rfam-seed', 'db', family, family + '.db')
    # create dir along the path if not exists
    db_path = os.path.dirname(output_db)
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    with open(output_db, 'w') as handle:
        SeqIO.write(alt_records, handle, 'fasta')

POOL_SIZE = len(files)
pool = ThreadPool(processes=POOL_SIZE)

pool.map(worker, files)