import sys
from os.path import isfile, join, isdir, exists
from os import listdir
from random import shuffle
from sklearn.decomposition import PCA
import numpy as np
import scipy as sp

def save_file(header, names, scores, outfile):
    assert isinstance(header, str)
    with open(outfile, 'w') as handle:
        handle.write(header + '\n')
        for name, score in zip(names, scores):
            handle.write(name + '\t')
            for s in score:
                handle.write(str(s) + '\t')
            handle.write('\n')

file = 'Rfam-seed/combined.bitscore'

all_scores = []
all_names = []

tmp = set()
with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        all_names.append(name)
        all_scores.append(scores)
        if len(scores) == 58:
            print(line)

# get the 100 PC scores
print('PCA-lizing...')
components = 100
pca = PCA(n_components=components)
pca_scores = pca.fit_transform(all_scores)
header = '\t'.join(['PC' + str(i + 1) for i in range(components)])
save_file(header, all_names, pca_scores, 'Rfam-seed/combined.pcNorm100.bitscore')

# normalize the scores
print('Z-normalizing...')
def normalize(array):
    return sp.stats.mstats.zscore(array)

normalized_scores = []
for col in pca_scores.T:
    normalized_scores.append(normalize(col))

normalized_scores = np.array(normalized_scores).T
save_file(header, all_names, normalized_scores, 'Rfam-seed/combined.zNorm.pcNorm100.bitscore')
