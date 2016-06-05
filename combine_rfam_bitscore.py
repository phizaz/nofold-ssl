import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle, sample
from Bio import SeqIO
from optparse import OptionParser
import numpy as np
from sklearn.neighbors import BallTree
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from collections import Counter
from functools import partial
import sortedcontainers as sc
from operator import itemgetter
import time
import utils

'''
Combine the rfam seeds with the given query
this should be the first step of doing semi-supervised clustering
'''

parser = OptionParser(usage='cluster using semi-supervised label spreading algorithm')
parser.add_option('--query', action='store', default='query', dest='QUERY', help='the query name')
parser.add_option('--unformatted', action='store', default='false', dest="UNFORMATTED", help='is the query from somewhere else?')
parser.add_option('--cripple', action='store', type='int', dest='CRIPPLE', help='cripple degree')
parser.add_option('--sample', action='store', type='int', default=5, dest='SAMPLE', help='number of seed sequenecs shall be randomly taken from each family')
parser.add_option('--type', action='store', default='random', dest='TYPE', help='what kind of seed selection preferred?')
parser.add_option('--nn', action='store', type='int', default=7, dest='NN', help='number of nearest neighbors for closest seed selection')
parser.add_option('--small', action='store', default='false', dest='SMALL', help='take only the relevant seed families')
(opts, args) = parser.parse_args()

# validate possible types
possible_types = {'high_density', 'closest', 'random'}
if opts.TYPE not in possible_types:
    print('not recornized type')
    print('possible types:', possible_types)
    sys.exit()

# validate sample parameter
if opts.TYPE in {'high_density', 'random'}:
    if opts.SAMPLE <= 0:
        print('sample count is not proper')
        sys.exit()

path = 'Rfam-seed/db'
query = opts.QUERY

families = utils.get_all_families()

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
    if not utils.check_family(family):
        return []

    file = join(path, family, family + '.bitscore')
    sequences, _ = get_sequences_from_file(file, cols)
    return sequences

def get_high_dense_seed_sequences(family, total=5, cols=None):
    if not utils.check_family(family):
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
    if not utils.check_family(family):
        return []

    sequences = get_seed_sequences(family, cols)
    return sample(sequences, min(total, len(sequences)))

def get_centroid_seed_sequences(family, cols=None):
    if not utils.check_family(family):
        return []

    sequences = get_seed_sequences(family, cols)
    names, _points = list(zip(*sequences))
    points = np.array(_points)

    centroid = np.zeros(points[0].shape)
    for point in points:
        centroid += point
    centroid /= len(points)

    return (family + '_centroid', centroid)

all_sequences = []

# get scores from the query
query_file = join('Rfam-seed', query, query + '.bitscore')
query_sequences, query_header_cols = get_sequences_from_file(query_file)
print('query cols count:', len(query_header_cols))

all_sequences += query_sequences

available_families = set(utils.get_calculated_families())

if opts.UNFORMATTED == 'true':
    print('unformatted is "true"')
    print('taking from all we have')
    seed_families = available_families
else:
    # get querying families, not having families
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
    print(not_having_families)

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
print('always include centroids...')
if opts.TYPE == 'high_density':
    print('sample will be taken from high denisty areas...', opts.SAMPLE, 'samples per families')
elif opts.TYPE == 'random':
    print('sample will be taken randomly...', opts.SAMPLE, 'samples per families')
elif opts.TYPE == 'closest':
    print('only closest:', opts.NN, 'neighbors seeds to queries will be taken...')

if opts.TYPE in {'random', 'high_density'}:
    for family in seed_families:
        if opts.TYPE == 'random':
            all_sequences += get_random_seed_sequences(family, total=opts.SAMPLE, cols=query_header_cols)
        elif opts.TYPE == 'high_density':
            all_sequences += get_high_dense_seed_sequences(family, total=opts.SAMPLE, cols=query_header_cols)
elif opts.TYPE in {'closest'}:
    all_query_names = list(map(lambda x: x[0], query_sequences))
    all_query_points = list(map(lambda x: x[1], query_sequences))

    # using sorted list
    # query_points_closests = [sc.SortedListWithKey(key=itemgetter(0)) for i in range(len(all_query_points))]
    query_points_closests = [[] for i in range(len(all_query_points))]

    def get_query_point_closests_by_family(family):
        # finding kNN from each family and them combine is a way to save memory, but slower !
        seed_sequences = get_seed_sequences(family, cols=query_header_cols)
        seed_names = list(map(lambda x: x[0], seed_sequences))
        seed_points = list(map(lambda x: x[1], seed_sequences))

        nearest_seed = BallTree(seed_points)
        k = min(opts.NN, len(seed_points))
        p_dists, p_idxs = nearest_seed.query(all_query_points, k=k)

        results = [[] for i in range(len(all_query_points))]
        for query_idx, (dists, idxs) in enumerate(zip(p_dists, p_idxs)):
            closest_seed_names = list(map(lambda x: seed_names[x], idxs))
            closest_seed_points = list(map(lambda x: seed_points[x], idxs))
            results[query_idx] += list(zip(dists, closest_seed_names, closest_seed_points))
        return results

    def remove_excess():
        for each in query_points_closests:
            each.sort(key=itemgetter(0))
            del each[opts.NN:]

    print('load sequences and find local KNN and merge and sort and delete excess elements from the result in real time..')
    time_start = time.time()
    pool = Pool(int(cpu_count()))
    local_query_points_closests = []
    cleanup_loops = 100
    for i, each in enumerate(pool.imap_unordered(get_query_point_closests_by_family, seed_families), 1):
        print('family:', i, 'of', len(seed_families))
        for all, local in zip(query_points_closests, each):
            all += local
            # # delete the excess elements
            # del all[opts.NN:]

        if i % cleanup_loops == 0:
            print('cleaning up...')
            remove_excess()
    remove_excess()

    pool.close()
    time_stop = time.time()
    print('time elapsed:', time_stop - time_start)

    print('getting selected seed sequences')
    selected_seed = {}
    selected_seed_by_family = Counter()
    for each in query_points_closests:
        for dist, name, point in each:
            if name not in selected_seed:
                family, _ = name.split('_')
                selected_seed_by_family[family] += 1
                selected_seed[name] = point
    print('seed count:', len(selected_seed))
    print('seed by family:', selected_seed_by_family)

    selected_seed_sequences = []
    for name, point in selected_seed.items():
        selected_seed_sequences.append((name, point))

    all_sequences += selected_seed_sequences

else:
    print('type is not correct')
    sys.exit()

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
