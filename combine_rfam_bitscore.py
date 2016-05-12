import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle

path = 'Rfam-seed/db'

families = [f for f in listdir(path) if isdir(join(path, f))]

def check_family(family):
    expected_file = join(path, family, family + '.bitscore')
    return exists(expected_file)

def get_header(family):
    file = join(path, family, family + '.bitscore')
    with open(file, 'r') as handle:
        header = handle.readline().strip()
    return header

def get_sequences_from_file(file):
    sequences = []
    with open(file, 'r') as handle:
        # discard the header
        handle.readline()
        for line in handle:
            line = line.strip()
            tokens = line.split('\t')
            name, scores = tokens[0], list(map(float, tokens[1:]))
            sequences.append((name, scores))
    return sequences

def get_seed_sequences(family):
    if not check_family(family):
        return []

    file = join(path, family, family + '.bitscore')
    return get_sequences_from_file(file)

def get_seed_some_sequences(family, total=5):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family)

    if len(sequences) < total:
        print('not enough sequences in family:', family, 'it has only:', len(sequences))

    # take randomly
    shuffle(sequences)
    return sequences[:total]

# get some sequences from each seeding family
all_sequences = []
for family in families:
    all_sequences += get_seed_some_sequences(family, total=5)

# also get sequences from the query file as well
# query_file = 'Rfam-seed/Rfam-query.bitscore'
# all_sequences += get_sequences_from_file(query_file)

# save to file
header = get_header('RF00001')
outfile = 'Rfam-seed/Rfam-combined.bitscore'
with open(outfile, 'w') as handle:
    handle.write(header + '\n')
    for name, scores in all_sequences:
        handle.write(name + '\t')
        for score in scores:
            handle.write(str(score) + '\t')
        handle.write('\n')

print(len(all_sequences))




