import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from Bio import SeqIO

'''
Get the families (that is required by the query) that have no bitscores (not calculated yet!)
'''

path = 'Rfam-seed/db'

families = [f for f in listdir(path) if isdir(join(path, f))]

def check_family(family):
    expected_file = join(path, family, family + '.bitscore')
    return exists(expected_file)

available_families = set(filter(check_family, families))

query_file = 'Rfam-seed/query/query.db'
count = 0
not_having_families = set()
with open(query_file, 'r') as handle:
    records = SeqIO.parse(handle, 'fasta')
    for record in records:
        family = record.name.split('_')[0][1:]
        if family not in available_families and family not in not_having_families:
            not_having_families.add(family)
            print('not having:', family)
            count += 1

print('total not having:', count)
