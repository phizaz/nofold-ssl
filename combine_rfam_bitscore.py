import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle, sample
from Bio import SeqIO
from optparse import OptionParser
import numpy as np

'''
Combine the rfam seeds with the given query
this should be the first step of doing semi-supervised clustering
'''

parser = OptionParser(usage='cluster using semi-supervised label spreading algorithm')
parser.add_option('--query', action='store', default='query', dest='QUERY', help='the query name')
parser.add_option('--unformatted', action='store', default='false', dest="UNFORMATTED", help='is the query from somewhere else?')
parser.add_option('--cripple', action='store', type='int', dest='CRIPPLE', help='cripple degree')
parser.add_option('--sample', action='store', type='int', default=5, dest='SAMPLE', help='number of seed sequenecs shall be randomly taken from each family')
parser.add_option('--inc_centroid', action='store', default='false', dest='INC_CENTROID', help='should include cetroid ?')
parser.add_option('--high_density', action='store', default='false', dest='HIGH_DENSITY', help='should samples be selected from high density profile ?')
parser.add_option('--small', action='store', default='false', dest='SMALL', help='take only the relevant seed families')
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

def get_sequences_from_file(file, cols=None):
    sequences = []
    with open(file, 'r') as handle:
        # discard the header
        header_cols = handle.readline().strip().split('\t')
        header_cols_idx = [i for i in range(len(header_cols))]
        map_header_idx = dict(zip(header_cols, header_cols_idx))

        if cols is None:
            cols = header_cols

        only_cols = [col for col in cols if col in map_header_idx]
        only_cols_idx = set(map_header_idx[col] for col in only_cols)
        for line in handle:
            line = line.strip()
            tokens = line.split('\t')
            name, scores = tokens[0], list(map(float, tokens[1:]))
            only_scores = [scores[i] for i in range(len(scores)) if i in only_cols_idx]
            sequences.append((name, only_scores))
    return sequences, header_cols

def get_seed_sequences(family, cols=None):
    if not check_family(family):
        return []

    file = join(path, family, family + '.bitscore')
    sequences, _ = get_sequences_from_file(file, cols)
    return sequences

def get_high_dense_seed_sequences(family, total=5, cols=None):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family, cols)
    names, _points = list(zip(*sequences))
    points = np.array(_points)

    # if len(sequences) < total:
    #    print('not enough sequences in family:', family, 'it has only:', len(sequences))

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

def get_random_seed_sequences(family, total=5, cols=None):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family, cols)
    return sample(sequences, min(total, len(sequences)))

def get_centroid_seed_sequences(family, cols=None):
    if not check_family(family):
        return []

    sequences = get_seed_sequences(family, cols)
    names, _points = list(zip(*sequences))
    points = np.array(_points)

    centroid = np.zeros(points[0].shape)
    for point in points:
        centroid += point
    centroid /= len(points)

    return [(family + '_centorid', centroid)]

all_sequences = []

# get scores from the query
query_file = join('Rfam-seed', query, query + '.bitscore')
query_sequences, query_header_cols = get_sequences_from_file(query_file)
print('query cols count:', len(query_header_cols))

all_sequences += query_sequences

if opts.UNFORMATTED == 'true':
    print('unformatted is "true"')
    print('taking from all we have')
    seed_families = set(filter(check_family, families))
else:
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
    if opts.SMALL == 'true':
        print('take as small seed families as possible...')
        seed_families = cripple_target_families - set(cripple_families)
    else:
        seed_families = available_families - set(cripple_families)
    print('taking from:', len(seed_families), '/', len(available_families))

# taking seeds
if opts.INC_CENTROID == 'true':
    print('including centroids')
if opts.SAMPLE > 0:
    print('taking randomly for:', opts.SAMPLE, 'samples per families')
if opts.HIGH_DENSITY == 'true':
    print('sample will be taken from high denisty areas...')
for family in seed_families:
    #all_sequences += get_high_dense_seed_sequences(family, total=3)
    sequences_available = len(get_seed_sequences(family, cols=query_header_cols))
    if opts.INC_CENTROID == 'true':
        all_sequences += get_centroid_seed_sequences(family, cols=query_header_cols)
    if opts.SAMPLE > 0:
        # avoid adding the centroid again
        if not (opts.INC_CENTROID == 'true' and sequences_available == 1):
            if opts.HIGH_DENSITY == 'true':
                all_sequences += get_high_dense_seed_sequences(family, total=opts.SAMPLE, cols=query_header_cols)
            else:
                all_sequences += get_random_seed_sequences(family, total=opts.SAMPLE, cols=query_header_cols)

# save to file
if opts.UNFORMATTED == 'true':
    outfile = 'Rfam-seed/combined.' + query + '.bitscore'
else:
    outfile = 'Rfam-seed/combined.' + query + '.cripple' + str(cripple_family_count) + '.bitscore'
with open(outfile, 'w') as handle:
    handle.write('\t'.join(query_header_cols) + '\n')
    for name, scores in all_sequences:
        handle.write(name + '\t')
        for score in scores:
            handle.write(str(score) + '\t')
        handle.write('\n')

print('total database size:', len(all_sequences))
