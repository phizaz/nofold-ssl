import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle, sample
from Bio import SeqIO
from optparse import OptionParser
import numpy as np

parser = OptionParser(usage='cluster using semi-supervised label spreading algorithm')
parser.add_option("--query", action="store", default='query', dest="QUERY", help="the query name")
parser.add_option("--cripple", action="store", type='int', default=8, dest="CRIPPLE", help="cripple degree")
parser.add_option("--sample", action="store", type='int', default=5, dest="SAMPLE", help="number of seed sequenecs shall be randomly taken from each family")
parser.add_option("--inc_centroid", action="store", default='false', dest="INC_CENTROID", help="should include cetroid ?")
(opts, args) = parser.parse_args()

path = 'Rfam-seed/db'
query = opts.QUERY

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

def get_high_dense_seed_sequences(family, total=5):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family)
    names, _points = list(zip(*sequences))
    points = np.array(_points)

    if len(sequences) < total:
        print('not enough sequences in family:', family, 'it has only:', len(sequences))

    def dist(a, b):
        return np.linalg.norm(a - b)

    def average_dist(points, origin):
        s = 0
        for point in points:
            d = dist(point, origin)
            s += d
        avg_dist = s / len(points)
        return avg_dist

    def retain_high_density(names, points, retaining):
        avg_dists = [(name, origin, average_dist(points, origin)) for name, origin in zip(names, points)]
        sorted_dists = sorted(avg_dists, key=lambda x: x[2])
        retained = list(map(lambda x: (x[0], x[1]), sorted_dists[:retaining]))
        return retained

    # take only the most dense
    high_density_sequences = retain_high_density(names, points, retaining=total)
    return high_density_sequences

def get_random_seed_sequences(family, total=5):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family)
    return sample(sequences, min(total, len(sequences)))

def get_centroid_seed_sequences(family):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family)
    names, _points = list(zip(*sequences))
    points = np.array(_points)

    centroid = np.zeros(points[0].shape)
    for point in points:
        centroid += point
    centroid /= len(points)

    return [(family + '_centorid', centroid)]

# get querying families, not having families
available_families = set(filter(check_family, families))
query_database = join('Rfam-seed', query, query + '.db')
query_families = set()
with open(query_database, 'r') as handle:
    records = SeqIO.parse(handle, 'fasta')
    for record in records:
        family = record.name.split('_')[0][1:]
        query_families.add(family)
print('families required by the query:', len(query_families))
not_having_families = query_families - available_families
print('families we don\'t have:', len(not_having_families))

all_sequences = []

# get scores from the query
query_file = join('Rfam-seed', query, query + '.bitscore')
all_sequences += get_sequences_from_file(query_file)

# get some scores from each seeding family (except the marked as crippled)
cripple_family_count = opts.CRIPPLE
print('cripple count:', cripple_family_count)
cripple_more = cripple_family_count - len(not_having_families)
if cripple_more < 0:
    print('cannot attain the target cripple count!')
    sys.exit()
print('more to be crippled:', cripple_more)
cripple_target_families = query_families - not_having_families
cripple_families = sample(cripple_target_families, cripple_more)
print('marked as crippled:', cripple_families)
seed_families = available_families - set(cripple_families)
print('taking from:', len(seed_families), '/', len(available_families))
if opts.INC_CENTROID == 'true':
    print('including centroids')
if opts.SAMPLE > 0:
    print('taking randomly for:', opts.SAMPLE)
for family in seed_families:
    #all_sequences += get_high_dense_seed_sequences(family, total=3)
    sequences_available = len(get_seed_sequences(family))
    if opts.INC_CENTROID == 'true':
        all_sequences += get_centroid_seed_sequences(family)
    if opts.SAMPLE > 0:
        # avoid adding the centroid again
        if not (opts.INC_CENTROID == 'true' and sequences_available == 1):
            all_sequences += get_random_seed_sequences(family, total=opts.SAMPLE)

# save to file
header = get_header('RF00001')
outfile = 'Rfam-seed/combined.' + query + '.cripple' + str(cripple_family_count) + '.bitscore'
with open(outfile, 'w') as handle:
    handle.write(header + '\n')
    for name, scores in all_sequences:
        handle.write(name + '\t')
        for score in scores:
            handle.write(str(score) + '\t')
        handle.write('\n')

print('total database size:', len(all_sequences))
