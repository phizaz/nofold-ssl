from __future__ import division
from optparse import OptionParser
from collections import Counter
import numpy as np
from operator import itemgetter

def transform():
    pass

def get_clusters(lines):
    clusters = []
    for line in lines:
        names = line.strip().split()
        clusters.append(names)
    return clusters

def get_names(clusters):
    names_by_family = {}
    for names in clusters:
        for name in names:
            family, _ = name.split('_')

            if family not in names_by_family:
                names_by_family[family] = []
            names_by_family[family].append(name)
    return names_by_family


def is_dominated_by(family, cluster):
    counter = Counter()
    for name in cluster:
        fam, _ = name.split('_')
        counter[fam] += 1
    dominant_family, cnt = counter.most_common(1).pop()
    return family == dominant_family, cnt

def sensitivity_of(family, clusters, names_by_family):
    dominating_cnt = 0
    for cluster in clusters:
        dominating, cnt = is_dominated_by(family, cluster)
        if dominating:
            dominating_cnt += cnt

    all_cnt = len(names_by_family[family])
    return dominating_cnt / all_cnt

def precision_of(family, clusters, names_by_family):
    dominating_cnt = 0
    all_cnt = 0
    for cluster in clusters:
        dominating, cnt = is_dominated_by(family, cluster)
        if dominating:
            dominating_cnt += cnt
            all_cnt += len(cluster)
    if all_cnt == 0:
        return 0
    return dominating_cnt / all_cnt

def family_cnt_in_cluster(family, cluster):
    counter = Counter()
    for name in cluster:
        fam, _ = name.split('_')
        counter[fam] += 1
    return counter[family]

def max_in_cluster_of(family, clusters, names_by_family):
    cnt = max(family_cnt_in_cluster(family, cluster) for cluster in clusters)
    all_cnt = len(names_by_family[family])
    return cnt / all_cnt

parser = OptionParser(usage='evaluate the clustering results')
parser.add_option('--file', action='store', dest='FILE', help='cluster result file')
parser.add_option('--nofold', action='store', default='false', dest='NOFOLD', help='is the result from original NoFold ?')
(opts, args) = parser.parse_args()

print('evaluating form file:', opts.FILE)

clusters = []
with open(opts.FILE, 'r') as handle:
    if opts.NOFOLD == 'true':
        print('transforming nofold result ...')
        lines = []
        handle.readline()
        for line in handle:
            tokens = line.strip().split('\t')
            names = tokens[4].strip().split(',')
            lines.append('\t'.join(names))
    else:
        lines = handle.readlines()

    clusters = get_clusters(lines)

print('number of sequences:', sum(len(names) for names in clusters))
print('number of clusters:', len(clusters))

names_by_family = get_names(clusters)
print('number of families:', len(names_by_family))

families = names_by_family.keys()
results = []
for family in sorted(families):
    results.append((
        family,
        sensitivity_of(family, clusters, names_by_family),
        precision_of(family, clusters, names_by_family),
        max_in_cluster_of(family, clusters, names_by_family)
    ))

output_file = opts.FILE + '.evaluation'
with open(output_file, 'w') as handle:
    col_names = ['sensitivity', 'precision', 'max_in_cluster']
    handle.write('\t'.join(['family'] + col_names) + '\n')
    for cols in results:
        handle.write('\t'.join(map(str, cols)) + '\n')

    sensitivities = np.array(map(itemgetter(1), results))
    precisions = np.array(map(itemgetter(2), results))
    max_in_clusters = np.array(map(itemgetter(3), results))

    handle.write('\t'.join(map(lambda x: 'avg_' + x, col_names)) + '\n')
    handle.write('\t'.join(map(str,
                               [
                                   sensitivities.mean(),
                                   precisions.mean(),
                                   max_in_clusters.mean()
                               ])) + '\n')

print('done!')