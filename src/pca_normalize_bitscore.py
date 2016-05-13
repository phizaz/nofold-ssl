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

file = 'Rfam-seed/Rfam-combined.bitscore'

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

# get the 100 PC scores
print('PCA-lizing...')
components = 100
pca = PCA(n_components=components)
pca.fit(all_scores)
pca_scores = pca.transform(all_scores)
header = '\t'.join(['PC' + str(i + 1) for i in range(components)])
save_file(header, all_names, pca_scores, 'Rfam-seed/Rfam-combined.pcNorm100.bitscore')

# normalize the scores
print('Z-normalizing...')
def normalize(array):
    return sp.stats.mstats.zscore(array)

normalized_scores = []
for col in pca_scores.T:
    normalized_scores.append(normalize(col))

normalized_scores = np.array(normalized_scores).T
save_file(header, all_names, normalized_scores, 'Rfam-seed/Rfam-combined.zNorm.pcNorm100.bitscore')
