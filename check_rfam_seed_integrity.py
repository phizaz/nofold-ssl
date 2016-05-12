import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from Bio import SeqIO
from multiprocessing.dummy import Pool as ThreadPool

path = 'Rfam-seed/db'

families = [f for f in listdir(path) if isdir(join(path, f))]

def check_family(family):
    expected_file = join(path, family, family + '.zNorm.bitscore')
    return exists(expected_file)

print('list of unfinished families:')
for family in families:
    if not check_family(family):
        print(family)
