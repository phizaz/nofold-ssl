from __future__ import print_function

'''
Further refine clusters from inital label propagation by splitting and merging
Splitting using the local inter-cluster distance criteria
Merging using the supervised merging techninque (merge those clusters having the same neareast 'seed' centroid)
'''


def point_of(name):
    return sequences[name]


def points_of(names):
    return map(point_of, names)


def retain_high_density(names, portion=0.9):
    points = list(map(point_of, names))
    take_out = int((1 - portion) * len(points))
    retaining = len(points) - take_out
    avg_dists = [(name, average_dist(points, origin)) for name, origin in zip(names, points)]
    sorted_dists = sorted(avg_dists, key=lambda x: x[1])
    retained = list(map(lambda x: x[0], sorted_dists[:retaining]))
    return retained


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

def split_cluster(cluster, clusters, C):
    import utils.helpers.space as space
    assert isinstance(cluster, space.Cluster)
    assert all(isinstance(cluster, space.Cluster) for cluster in clusters)



def split_clusters(clusters, C):
    from multiprocessing import Pool
    from functools import partial
    print('splitting clusters...')
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





if __name__ == '__main__':
    import utils
    import argparse
    import sys
    from os.path import join
    import utils.helpers.space as space

    parser = argparse.ArgumentParser(usage='further clustering using inter-cluster distance criteria')
    parser.add_argument('--tag', required=True, help='tag')
    parser.add_argument('--alg', help='task\'s algorithm description')
    parser.add_argument('--components', type=int, default=100, help='PCAs number of components')
    parser.add_argument('--C', type=float, default=1.0, help='splitting cluster parameter')
    args = parser.parse_args()

    score_file = join(utils.path.results_path(), 'combined.{}.pcNorm{}.zNorm.bitscore'.format(
        args.tag, args.components
    ))
    cluster_file = join(utils.path.results_path(), 'combined.{}.{}.cluster'.format(args.tag, args.alg))

    print('loading score file')
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(score_file)

    # get seed clusters
    seed_groups = utils.modify.group_bitscore_by_family(seed_names, seed_points)

    print('calculating centroids for seed clusters..')
    seed_centroids = {}
    for fam, points in seed_groups.items():
        seed_centroids[fam] = space.centroid_of(points)

    closest_seed_centroid = space.ClosestPoint(seed_centroids.values(), seed_centroids.keys())

    print('loading cluster file:', cluster_file)
    clusters = utils.get.get_name_clusters(cluster_file)

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
