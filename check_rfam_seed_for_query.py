import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from Bio import SeqIO
import utils

'''
Get the families (that is required by the query) that have no bitscores (not calculated yet!)
'''

path = 'Rfam-seed/query/query.db'

def family_of(name):
    first = name.split('_')[0]
    if first[:2] == 'QR':
        return first[1:]
    else:
        return first

with open(path, 'r') as handle:
    records = SeqIO.parse(handle, 'fasta')
    required_families = set(map(family_of, map(lambda x: x.name, records)))

available_families = set(utils.get_calculated_families())
not_having_families = required_families - available_families

print('total not having:', len(not_having_families))
for fam in not_having_families:
    print(fam)
