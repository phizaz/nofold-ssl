import numpy as np
from sklearn.neighbors import BallTree
from itertools import combinations, product
from agglomerative_clustering import AgglomerativeClusteringMaxMergeDist
from os.path import join
from optparse import OptionParser

parser = OptionParser(usage='further clustering using inter-cluster distance criteria')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
parser.add_option("--alg", action="store", default='labelPropagation', dest="ALG", help="the file's algorithm description")
parser.add_option("--components", action="store", type='int', default=100, dest="COMPONENTS", help="PCA's number of components")
parser.add_option("--C", action="store", type='float', default=1.1, dest="C", help="splitting cluster parameter")
(opts, args) = parser.parse_args()

tag = opts.TAG
alg = opts.ALG
score_file = join('Rfam-seed', 'combined.' + tag + '.pcNorm' + str(opts.COMPONENTS) + '.zNorm.bitscore')
cluster_file = join('Rfam-seed', 'combined.' + tag + '.' + alg + '.cluster')

print('loading score file')
sequences = {}
with open(score_file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        sequences[name] = np.array(scores)

print('loading cluster file:', cluster_file)
clusters = []
with open(cluster_file, 'r') as handle:
    for line in handle:
        line = line.strip()
        names = line.split(' ')
        clusters.append(names)

def point_of(name):
    return sequences[name]

def dist(a, b):
    return np.linalg.norm(a - b)

def average_dist(points, origin):
    s = 0
    for point in points:
        d = dist(point, origin)
        s += d

    avg_dist = s / len(points)
    return avg_dist

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

def centroid_of(points):
    centroid = sum(points) / len(points)
    return centroid

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

def split_clusters(clusters, C):
    print('pruning clusters...')
    # pruned_clusters = list(map(retain_high_density, clusters))
    pruned_clusters = clusters

    print('further intra-clustering...')
    total_clusters = 0
    final_clusters = []
    for i, (names, pruned_names) in enumerate(zip(clusters, pruned_clusters)):
        local_inter_cluster_dist = C * min(dist_cluster_avg(pruned_names, pruned_cluster) for pruned_cluster in pruned_clusters[:i] + pruned_clusters[i+1:])
        print('local inter-cluster dist:', local_inter_cluster_dist)

        points = list(map(point_of, names))
        agg = AgglomerativeClusteringMaxMergeDist()
        labels = agg.fit(points, local_inter_cluster_dist, method='average', metric='euclidean')
        cluster_cnt = max(labels) + 1

        if cluster_cnt == 1:
            final_clusters.append(names)
        else:
            sub_clusters = labels_to_clusters(names, labels)
            final_clusters += sub_clusters

        total_clusters += cluster_cnt
    print('total clusters:', total_clusters)
    print('final_clusters count:', len(final_clusters))
    return final_clusters

final_clusters = split_clusters(clusters, C=opts.C)

print('saving final cluster to file...')
outfile = join('Rfam-seed', 'combined.' + tag + '.' + alg + '.refined.cluster')
with open(outfile, 'w') as handle:
    for members in final_clusters:
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')
print('saved!')