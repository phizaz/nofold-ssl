import sys
from os.path import isfile, join, isdir, exists
from os import listdir

path = 'Rfam-seed/db'

families = [f for f in listdir(path) if isdir(join(path, f))]

def check_family(family):
    expected_file = join(path, family, family + '.bitscore')
    return exists(expected_file)

print('list of unfinished families:')
count = 0
for family in families:
    if not check_family(family):
        print(family)
        count += 1

print('count:', count)
