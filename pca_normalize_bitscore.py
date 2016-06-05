import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle
from sklearn.decomposition import PCA
import numpy as np
import scipy as sp
from optparse import OptionParser
import bisect as bs
from Bio import SeqIO

'''
Normalize the combined bitscore using PCA and Z-normalizer
'''

def save_file(header, names, scores, outfile):
    assert isinstance(header, str)
    with open(outfile, 'w') as handle:
        handle.write(header + '\n')
        for name, score in zip(names, scores):
            handle.write(name + '\t')
            for s in score:
                handle.write(str(s) + '\t')
            handle.write('\n')

def normalize(l):
    return sp.stats.mstats.zscore(l)

def prepare_normalizer():

    def floater(cell):
        return 'NA' if cell == 'NA' else float(cell)

    def read_file(file):
        results = []
        with open(file, 'r') as handle:
            cols = handle.readline().strip().split()
            for line in handle:
                tokens = line.strip().split()
                # length_id = tokens[0]
                digits = map(floater, tokens[1:])
                results.append(dict(zip(cols, digits)))
        return results

    means_file = join('norm', 'varlen2.scale_means.txt')
    sds_file = join('norm', 'varlen2.scale_sds.txt')

    db_means = read_file(means_file)
    db_sds = read_file(sds_file)

    def possible_length(col):
        return map(lambda x: x[col] != 'NA', db_means)

    def transform(l):
        # l = [0, 1]* -> l = [1,3,5,9] according to the 1 positions
        results = []
        for i, each in enumerate(l):
            if each: results.append(i)
        return results

    cols = db_means[0].keys()
    increasing_list = map(possible_length, cols)
    possible_length_actual = dict(zip(cols, increasing_list))
    possible_length_list = dict(zip(cols, map(transform, increasing_list)))

    def closest_length(length, col):
        if length < len(possible_length_actual[col]) and possible_length_actual[col][length]:
            return length

        # print('col:', col, 'length:', length)
        pos = bs.bisect_left(possible_length_list[col], length)
        before = possible_length_list[col][pos]
        # it is more than we have
        if pos == len(possible_length_list[col]) - 1:
            return before

        # return the closest one
        after = possible_length_list[col][pos + 1]
        if length - before < after - length:
            return before
        else:
            return after

    def supervised_normalize(col, length, x):
        c_length = closest_length(length, col)
        return (x - db_means[c_length][col]) / db_sds[c_length][col]

    return supervised_normalize

def get_header(family):
    path = 'Rfam-seed/db'
    file = join(path, family, family + '.bitscore')
    with open(file, 'r') as handle:
        header = handle.readline().strip()
    return header

parser = OptionParser(usage='further clustering using inter-cluster distance criteria')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
parser.add_option('--query', action='store', dest='QUERY', help='db file')
parser.add_option('--lengthnorm', action='store', dest='LENGTH_NORM', default='false', help='whether to use length normalization?')
parser.add_option("--components", action="store", type='int', default=100, dest="COMPONENTS", help="PCA's number of components")
(opts, args) = parser.parse_args()

file_name = 'combined.' + opts.TAG + '.bitscore'
no_extension_name = '.'.join(file_name.split('.')[:-1])
print('no_extension_name:', no_extension_name)
file = join('Rfam-seed', file_name)

all_scores = []
all_names = []

with open(file, 'r') as handle:
    full_header = handle.readline().strip()
    cols = full_header.split()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        all_names.append(name)
        all_scores.append(scores)

all_lens = set(map(len, all_scores))
all_scores = np.array(all_scores)

if len(all_lens) > 1:
    print('all_lens:', all_lens)
    print('dimension not consistent')
    sys.exit()

# Z-normalize according to lengths
if opts.LENGTH_NORM == 'true':
    print('Supervised Z-normalizing according to length...')
    def prepare_length_of(all_names):
        def open_file(file):
            with open(file, 'r') as handle:
                records = SeqIO.parse(handle, 'fasta')
                length_name = {}
                for record in records:
                    length_name[record.name] = len(record.seq)
            return length_name

        length_name = {}

        db_file = join('Rfam-seed', opts.QUERY, opts.QUERY + '.db')
        files = [db_file]

        all_families = set()
        for name in all_names:
            fam = name.split('_')[0]
            if fam[:2] == 'RF':
                # don't add QRF
                all_families.add(fam)
        print('families involved:', all_families)

        for family in all_families:
            file = join('Rfam-seed', 'db', family, family + '.db')
            files.append(file)

        for file in files:
            length_name.update(open_file(file))

        def length_of(name):
            return length_name[name]

        return length_of

    length_of = prepare_length_of(all_names)
    assert hasattr(length_of, '__call__')
    supervised_normalize = prepare_normalizer()
    assert hasattr(supervised_normalize, '__call__')
    z_length_normalized_scores = []
    for name, scores in zip(all_names, all_scores):
        row = []
        for col, digit in zip(cols, scores):
            row.append(supervised_normalize(col, length_of(name), digit))
        z_length_normalized_scores.append(row)
    save_file(full_header, all_names, z_length_normalized_scores, join('Rfam-seed', no_extension_name + '.zNorm.bitscore'))
    # patch the score back, and feed it to the next step
    all_scores = z_length_normalized_scores

# get the 100 PC scores
print('PCA-lizing...')
components = opts.COMPONENTS
header = '\t'.join(['PC' + str(i + 1) for i in range(components)])
pca = PCA(n_components=components)
pca_scores = pca.fit_transform(all_scores)
save_file(header, all_names, pca_scores, join('Rfam-seed', no_extension_name + '.pcNorm' + str(components) + '.bitscore'))

# normalize the PC scores
print('Z-normalizing for PC' + str(opts.COMPONENTS))
pc_normalized_scores = []
for col in pca_scores.T:
    pc_normalized_scores.append(normalize(col))
pc_normalized_scores = np.array(pc_normalized_scores).T
save_file(header, all_names, pc_normalized_scores, join('Rfam-seed', no_extension_name + '.pcNorm' + str(components) + '.zNorm.bitscore'))
