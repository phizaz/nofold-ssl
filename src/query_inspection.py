from os.path import join
from optparse import OptionParser
from fastcluster import linkage
import numpy as np
from itertools import product, combinations
from sklearn.neighbors import BallTree

raise NotImplemented # need refactoring

def family_of(name):
    first, rest = name.split('_')
    if first[0] == 'Q':
        return first[1:]
    else:
        return first

def dist(a, b):
    return np.linalg.norm(a - b)

def dist_cluster_avg(points_A, points_B):
    s = sum(dist(a, b) for a, b in product(points_A, points_B))
    return s / float(len(points_A) * len(points_B))

def centroid_of(points):
    centroid = sum(points) / len(points)
    return centroid

def dist_cluster_centroid(points_A, points_B):
    centroid_A = centroid_of(points_A)
    centroid_B = centroid_of(points_B)
    return dist(centroid_A, centroid_B)

parser = OptionParser(usage='cluster using semi-supervised label propagation algorithm')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
parser.add_option("--components", action="store", type='int', default=100, dest="COMPONENTS", help="PCA's number of components")
(opts, args) = parser.parse_args()

tag = opts.TAG
file = join('../results', 'combined.' + tag + '.pcNorm' + str(opts.COMPONENTS) + '.zNorm.bitscore')

names = []
points = []

query_names = []
query_points = []

with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))

        if name[:2] == 'RF':
            names.append(name)
            points.append(scores)
        else:
            query_names.append(name)
            query_points.append(scores)

clusters = {}
for name, point in zip(names, points):
    family = family_of(name)
    if family not in clusters:
        clusters[family] = []
    clusters[family].append(np.array(point))

centroids = {}
for family, points in clusters.items():
    centroids[family] = centroid_of(points)

closest_centroid = BallTree(centroids.values())

query_clusters = {}
for name, point in zip(query_names, query_points):
    family = family_of(name)
    if family not in query_clusters:
        query_clusters[family] = []
    query_clusters[family].append(np.array(point))

query_centroids = {}
for family, points in query_clusters.items():
    query_centroids[family] = centroid_of(points)

closest_query_centroid = BallTree(query_centroids.values())

def find_largest_merge_dist(clusters):
    # find the minimum distance to keep this in a single group
    largest_merge_dists = []
    for name, point in clusters.items():
        merge_hist = linkage(point, method='average', metric='euclidean', preserve_input=True)
        merge_dist = list(reversed([each[2] for each in merge_hist]))
        if len(merge_dist) > 0:
            largest_merge = merge_dist[0]
            largest_merge_dists.append(largest_merge)
    largest_merge_dists.sort()
    largest_merge_dists = list(reversed(largest_merge_dists))
    return largest_merge_dists

print('largest merge dist:', find_largest_merge_dist(clusters))
print('query: largest merge dist:', find_largest_merge_dist(query_clusters))

for family, points in query_clusters.items():
    if family not in clusters:
        continue

    dist_to_seed = dist_cluster_centroid(points, clusters[family])

    # the closest centroid between seed and query is of the same family!
    _dist, _ = closest_centroid.query([centroid_of(points)])
    dist_to_closest = float(_dist)

    # the second closest centroid between query clusters is farther than the seed!
    _dist, _ = closest_query_centroid.query([centroid_of(points)], 2)
    dist_to_closest_query = float(_dist[0][1])

    print('dist:', dist_to_seed, dist_to_closest, dist_to_closest_query)

def find_distance_among_clusters(clusters):
    # distance between clusters
    min_cluster_dist = dict(zip(clusters, [float('INF') for i in range(len(clusters))]))
    for (family_A, points_A), (family_B, points_B) in combinations(clusters.items(), 2):
        min_cluster_dist[family_A] = min(dist_cluster_avg(points_A, points_B), min_cluster_dist[family_A])
    largest_min_cluster_dist = list(reversed(sorted(min_cluster_dist.values())))
    return largest_min_cluster_dist
