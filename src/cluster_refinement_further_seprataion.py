import numpy as np
from sklearn.neighbors import BallTree, KNeighborsClassifier
from sklearn.semi_supervised import LabelPropagation
from itertools import combinations, product
from agglomerative_clustering import AgglomerativeClusteringMaxMergeDist
from os.path import join
from optparse import OptionParser
from multiprocessing.pool import Pool
from functools import partial
from operator import itemgetter
from collections import Counter
import sys

'''
Further refine clusters from inital label propagation by splitting and merging
Splitting using the local inter-cluster distance criteria
Merging using the supervised merging techninque (merge those clusters having the same neareast 'seed' centroid)
'''

def point_of(name):
    return sequences[name]

def points_of(names):
    return map(point_of, names)

def create_map(strings):
    all_strings = set(strings)
    all_int = [i for i in range(len(all_strings))]
    str_to_int = dict(zip(all_strings, all_int))
    int_to_str = dict(zip(all_int, all_strings))

    def map_to_int(string):
        return str_to_int[string]

    def map_to_str(int):
        return int_to_str[int]

    return map_to_int, map_to_str

def is_seed(name):
    first = name.split('_')[0]
    return first[:2] == 'RF'

def family_of(name):
    first = name.split('_')[0]
    if first[0] == 'Q':
        return first[1:]
    else:
        return first

def dist(a, b):
    return np.linalg.norm(a - b)

def average_dist(points, origin):
    s = 0
    for point in points:
        d = dist(point, origin)
        s += d
    avg_dist = s / len(points)
    return avg_dist

def centroid_of(points):
    centroid = sum(points) / len(points)
    return centroid

def retain_high_density(names, portion=0.9):
    points = list(map(point_of, names))
    take_out = int((1 - portion) * len(points))
    retaining = len(points) - take_out
    avg_dists = [(name, average_dist(points, origin)) for name, origin in zip(names, points)]
    sorted_dists = sorted(avg_dists, key=lambda x: x[1])
    retained = list(map(lambda x: x[0], sorted_dists[:retaining]))
    return retained

def dist_cluster_min(A, B):
    points_A = list(map(point_of, A))
    points_B = list(map(point_of, B))
    ballTree = BallTree(points_A)
    d, i = ballTree.query(points_B)
    return float(min(d))

def dist_cluster_avg(A, B):
    points_A = list(map(point_of, A))
    points_B = list(map(point_of, B))
    s = sum(dist(a, b) for a, b in product(points_A, points_B))
    return s / float(len(points_A) * len(points_B))

def dist_cluster_centroid(A, B):
    points_A = list(map(point_of, A))
    points_B = list(map(point_of, B))
    centroid_A = centroid_of(points_A)
    centroid_B = centroid_of(points_B)
    return dist(centroid_A, centroid_B)

def labels_to_clusters(names, labels):
    cluster_cnt = max(labels) + 1
    sub_clusters = [[] for i in range(cluster_cnt)]
    for name, label in zip(names, labels):
        sub_clusters[label].append(name)
    return sub_clusters

def total_sequences(clusters):
    return sum(len(names) for names in clusters)


def split_cluster((i, names), clusters, C):
    local_inter_cluster_dist = C * min(dist_cluster_avg(names, cluster) for cluster in clusters[:i] + clusters[i + 1:])
    # print('local inter-cluster dist:', local_inter_cluster_dist)

    points = list(map(point_of, names))
    agg = AgglomerativeClusteringMaxMergeDist()
    labels = agg.fit(points, local_inter_cluster_dist, method='average', metric='euclidean')
    cluster_cnt = max(labels) + 1

    if cluster_cnt == 1:
        return [names]
    else:
        return labels_to_clusters(names, labels)

def split_clusters(clusters, C):
    print('splitting clusters...')
    total_clusters = 0
    final_clusters = []

    pool = Pool()
    partial_fn = partial(split_cluster, clusters=clusters, C=C)
    splitted_clusters = pool.map(partial_fn, enumerate(clusters))
    pool.close()

    for each in splitted_clusters:
        final_clusters += each

    print('final_clusters count:', len(final_clusters))
    return final_clusters

def merge_clusters(families, closest_seed_centroid, clusters):
    print('mergining clusters...')
    merged_clusters = {}
    for names in clusters:
        points = list(map(point_of, names))
        centroid = centroid_of(points)
        _dist, _idx = closest_seed_centroid.query([centroid], 1)
        closest_dist = float(_dist)
        closest_family_idx = int(_idx)
        closest_family = families[closest_family_idx]

        if closest_family not in merged_clusters:
            merged_clusters[closest_family] = []
        merged_clusters[closest_family] += names

    result_clusters = merged_clusters.values()
    print('merged left', len(result_clusters), 'clusters')
    return result_clusters

def merge_clusters_label_propagation(seed_clusters, clusters):
    seeds_points = []
    seeds_labels = []
    for family, points in seed_clusters.items():
        seeds_points.append(centroid_of(points))
        seeds_labels.append(family)

    to_int, to_str = create_map(seeds_labels)
    int_labels = map(to_int, seeds_labels)

    unknown_points = []
    unknown_clusters = []
    for clust_id, names in enumerate(clusters):
        points = points_of(names)
        unknown_points += points
        unknown_clusters += [clust_id for i in range(len(points))]

    points = seeds_points + unknown_points
    labels = int_labels + [-1 for i in range(len(unknown_points))]

    ssl = LabelPropagation(kernel='rbf', gamma=0.5)
    ssl.fit(points, labels)

    predicted_labels = ssl.transduction_[len(seeds_points):]
    counters = [Counter() for i in range(len(clusters))]
    for label, cluster in zip(predicted_labels, unknown_clusters):
        counters[cluster][label] += 1

    cluster_labels = map(lambda x: x.most_common(1).pop()[0], counters)
    # print(cluster_labels)

    merged_clusters = {}
    for label, names in zip(cluster_labels, clusters):
        if label not in merged_clusters:
            merged_clusters[label] = []
        merged_clusters[label] += names

    result_clusters = merged_clusters.values()
    print('merged left', len(result_clusters), 'clusters')
    return result_clusters

def merge_clusters_knn(seed_clusters, clusters):
    seeds_points = []
    seeds_labels = []
    for family, points in seed_clusters.items():
        seeds_points.append(centroid_of(points))
        seeds_labels.append(family)

    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(seeds_points, seeds_labels)

    predicted_labels = []
    for names in clusters:
        points = points_of(names)
        labels = knn.predict(points)
        counter = Counter(labels)
        label, cnt = counter.most_common(1).pop()
        predicted_labels.append(label)

    merged_clusters = {}
    for label, names in zip(predicted_labels, clusters):
        if label not in merged_clusters:
            merged_clusters[label] = []
        merged_clusters[label] += names

    result_clusters = merged_clusters.values()
    print('merged left', len(result_clusters), 'clusters')
    return result_clusters

def identical_clusters(A, B):
    if len(A) != len(B):
        return False

    def tuplize(clusters):
        l = []
        for each in clusters:
            l.append(tuple(set(each)))
        return tuple(sorted(l))

    return tuplize(A) == tuplize(B)

parser = OptionParser(usage='further clustering using inter-cluster distance criteria')
parser.add_option('--tag', action='store', default='', dest='TAG', help='tag')
parser.add_option('--alg', action='store', default='labelPropagation', dest='ALG', help='the file algorithm description')
parser.add_option('--components', action='store', type='int', default=100, dest='COMPONENTS', help='PCAs number of components')
parser.add_option('--C', action='store', type='float', default=1.0, dest='C', help='splitting cluster parameter')
(opts, args) = parser.parse_args()

tag = opts.TAG
alg = opts.ALG
score_file = join('../results', 'combined.' + tag + '.pcNorm' + str(opts.COMPONENTS) + '.zNorm.bitscore')
cluster_file = join('../results', 'combined.' + tag + '.' + alg + '.cluster')

print('loading score file')
sequences = {}
with open(score_file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        sequences[name] = np.array(scores)

# get all seeds
all_seeds = []
for name, scores in sequences.items():
    family = family_of(name)
    if not is_seed(name):
        continue
    all_seeds.append((name, scores))

# get seed clusters
seed_clusters = {}
for name, scores in all_seeds:
    family = family_of(name)
    if family not in seed_clusters:
        seed_clusters[family] = []
    seed_clusters[family].append(scores)

print('calculating centroids for seed clusters..')
seed_centroids = []
seed_centroids_families = []
for family, points in seed_clusters.items():
    seed_centroids_families.append(family)
    seed_centroids.append(centroid_of(points))

closest_seed_centroid = BallTree(seed_centroids)

print('loading cluster file:', cluster_file)
clusters = []
with open(cluster_file, 'r') as handle:
    for line in handle:
        line = line.strip()
        names = line.split(' ')
        clusters.append(names)

splitted_clusters = split_clusters(clusters, C=opts.C)
for round in range(10):
    last_split_clusters = splitted_clusters
    print('round:', round + 1)
    merged_clusters = merge_clusters(seed_centroids_families, closest_seed_centroid, splitted_clusters)
    # merged_clusters = merge_clusters_label_propagation(seed_clusters, splitted_clusters)
    # merged_clusters = merge_clusters_knn(seed_clusters, splitted_clusters)
    splitted_clusters = split_clusters(merged_clusters, C=opts.C)

    if identical_clusters(last_split_clusters, splitted_clusters):
        break

final_clusters = splitted_clusters

print('saving final cluster to file...')
outfile = join('../results', 'combined.' + tag + '.' + alg + '.refined.cluster')
with open(outfile, 'w') as handle:
    for members in final_clusters:
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')
print('saved!')