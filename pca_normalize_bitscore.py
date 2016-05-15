import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle
from sklearn.decomposition import PCA
import numpy as np
import scipy as sp
from optparse import OptionParser

def save_file(header, names, scores, outfile):
    assert isinstance(header, str)
    with open(outfile, 'w') as handle:
        handle.write(header + '\n')
        for name, score in zip(names, scores):
            handle.write(name + '\t')
            for s in score:
                handle.write(str(s) + '\t')
            handle.write('\n')

parser = OptionParser(usage='further clustering using inter-cluster distance criteria')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
(opts, args) = parser.parse_args()

file_name = 'combined.' + opts.TAG + '.bitscore'
no_extension_name = '.'.join(file_name.split('.')[:-1])
print('no_extension_name:', no_extension_name)
file = join('Rfam-seed', file_name)

all_scores = []
all_names = []

with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        all_names.append(name)
        all_scores.append(scores)

        if len(scores) != 1973:
            print('dimension not consistent:', name)

all_lens = set(map(len, all_scores))
if len(all_lens) > 1:
    print('all_lens:', all_lens)
    print('dimension not consistent')
    sys.exit()

# get the 100 PC scores
print('PCA-lizing...')
components = 100
pca = PCA(n_components=components)
pca_scores = pca.fit_transform(all_scores)
header = '\t'.join(['PC' + str(i + 1) for i in range(components)])
save_file(header, all_names, pca_scores, join('Rfam-seed', no_extension_name + '.pcNorm100.bitscore'))

# normalize the scores
print('Z-normalizing...')
def normalize(array):
    return sp.stats.mstats.zscore(array)

normalized_scores = []
for col in pca_scores.T:
    normalized_scores.append(normalize(col))

normalized_scores = np.array(normalized_scores).T
save_file(header, all_names, normalized_scores, join('Rfam-seed', no_extension_name + '.zNorm.pcNorm100.bitscore'))
