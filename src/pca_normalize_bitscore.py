import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle
from sklearn.decomposition import PCA
import numpy as np
import scipy as sp
from optparse import OptionParser
import bisect as bs
import utils
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

def get_header(family):
    path = '../Rfam-seed/db'
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
file = join('../results', file_name)

names, points, header = utils.get_bitscores(file)

# Z-normalize according to lengths
if opts.LENGTH_NORM == 'true':
    from normalizer_length import LengthNormalizer

    print('Supervised Z-normalizing according to length...')
    normalizer = LengthNormalizer()
    length_normalized_points = normalizer.length_normalize_full(names, points, header, opts.QUERY)

    save_file('\t'.join(header), names, length_normalized_points, join('../results', no_extension_name + '.zNorm.bitscore'))
    # patch the score back, and feed it to the next step
    points = length_normalized_points

# get the 100 PC scores
print('PCA-lizing...')
components = opts.COMPONENTS
pc_header = '\t'.join(['PC' + str(i + 1) for i in range(components)])
pca = PCA(n_components=components)
pca_scores = pca.fit_transform(points)
save_file(pc_header, names, pca_scores, join('../results', no_extension_name + '.pcNorm' + str(components) + '.bitscore'))

# normalize the PC scores
print('Z-normalizing for PC' + str(opts.COMPONENTS))
pc_normalized_scores = []
for col in pca_scores.T:
    pc_normalized_scores.append(normalize(col))
pc_normalized_scores = np.array(pc_normalized_scores).T
save_file(pc_header, names, pc_normalized_scores, join('../results', no_extension_name + '.pcNorm' + str(components) + '.zNorm.bitscore'))
