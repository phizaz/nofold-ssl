import numpy as np
from sklearn.neighbors import BallTree
from itertools import combinations, product
from agglomerative_clustering import AgglomerativeClusteringMaxMergeDist

score_file = 'Rfam-seed/combined.zNorm.pcNorm100.bitscore'
cluster_file = 'Rfam-seed/combined.labelPropagation.cluster'

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

def retain_high_density(names, portion=0.8):
    points = list(map(point_of, names))
    take_out = int((1 - portion) * len(points))
    avg_dists = [(name, average_dist(points, origin)) for name, origin in zip(names, points)]
    sorted_dists = sorted(avg_dists, key=lambda x: -x[1])
    retained = list(map(lambda x: x[0], sorted_dists[take_out:]))
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
    s = sum(np.linalg.norm(a - b) for a, b in product(points_A, points_B))
    return s / float(len(points_A) * len(points_B))

def labels_to_clusters(names, labels):
    cluster_cnt = max(labels) + 1
    sub_clusters = [[] for i in range(cluster_cnt)]
    for name, label in zip(names, labels):
        sub_clusters[label].append(name)
    return sub_clusters

print('pruning clusters...')
pruned_clusters = list(map(retain_high_density, clusters))

# print('calculating the min dist between clusters...')
# min_inter_cluster_dist = min(dist_cluster_avg(a, b) for a, b in combinations(pruned_clusters, 2))
# print('min dist between cluster:', min_inter_cluster_dist)

print('further intra-clustering...')
total_clusters = 0
final_clusters = []
for i, names in enumerate(clusters):
    local_inter_cluster_dist = min(dist_cluster_avg(names, cluster) for cluster in pruned_clusters[:i] + pruned_clusters[i+1:])
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

print('saving final cluster to file...')
outfile = cluster_file + '.refined.cluster'
with open(outfile, 'w') as handle:
    for members in final_clusters:
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')
print('saved!')