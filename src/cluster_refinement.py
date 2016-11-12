from __future__ import print_function

'''
Further refine clusters from inital label propagation by splitting and merging
Splitting using the local inter-cluster distance criteria
Merging using the supervised merging techninque (merge those clusters having the same neareast 'seed' centroid)
'''


def split_cluster(cluster, clusters, C):
    from utils.helpers import space
    assert isinstance(cluster, space.Cluster)
    assert all(isinstance(cluster, space.Cluster) for cluster in clusters)

    if len(clusters) <= 1:
        return [cluster]  # just can't split

    clust_dist = [
        cluster.dist_avg(oth_clust)
        for oth_clust in clusters
        if cluster != oth_clust
        ]

    split_threshold = min(clust_dist) * C

    from utils.helpers.hclust import HierarchicalClustMaxMergeDist
    hclust = HierarchicalClustMaxMergeDist()
    split_labels = hclust.fit(cluster.points, split_threshold, method='average')
    labels_cnt = max(split_labels) + 1

    split_names = [[] for _ in range(labels_cnt)]
    split_points = [[] for _ in range(labels_cnt)]
    for name, point, label in zip(cluster.names, cluster.points, split_labels):
        split_names[label].append(name)
        split_points[label].append(point)

    new_clusters = []
    for names, points in zip(split_names, split_points):
        new_clusters.append(space.Cluster(names, points))

    return new_clusters


def split_clusters(clusters, C):
    from utils.helpers import space
    assert isinstance(clusters, list)
    assert all(isinstance(cluster, space.Cluster) for cluster in clusters)

    from multiprocessing import Pool
    from functools import partial

    print('splitting clusters...')
    pool = Pool()
    fn = partial(split_cluster, clusters=clusters, C=C)
    splitted_clusters = pool.map(fn, clusters)
    pool.close()

    all_clusts = []
    for each in splitted_clusters:
        all_clusts += each

    print('final clusters cnt:', len(all_clusts))
    return all_clusts


def merge_clusters(closest_family, clusters):
    from utils.helpers import space
    assert isinstance(closest_family, space.ClosestPoint)
    assert all(isinstance(clust, space.Cluster) for clust in clusters)

    print('merging clusters...')
    from collections import defaultdict
    clusts_by_fam = defaultdict(list)
    for clust in clusters:
        fam = closest_family.closest(space.centroid_of(clust.points))
        clusts_by_fam[fam].append(clust)

    all_clusts = []
    for fam, clusts in clusts_by_fam.items():
        if len(clusts) > 1:
            names = []
            points = []
            for clust in clusts:
                names += clust.names
                points += clust.points

            new_clust = space.Cluster(names, points)
            all_clusts.append(new_clust)
        else:
            clust = clusts.pop()
            all_clusts.append(clust)

    print('merged clusters cnt:', len(all_clusts))

    return all_clusts


def identical_clusters(A, B):
    assert isinstance(A, list)
    assert isinstance(B, list)
    from utils.helpers import space
    assert all(isinstance(clust, space.Cluster) for clust in A)
    assert all(isinstance(clust, space.Cluster) for clust in B)

    def prepare_name(names):
        return tuple(set(names))

    def prepare_clust(clust):
        return sorted(tuple(map(lambda x: prepare_name(x.names), clust)))

    AA = prepare_clust(A)
    BB = prepare_clust(B)

    return AA == BB


def run(clusters, seed_names, seed_points, c, merge):
    import utils
    # get seed clusters
    seed_groups = utils.modify.group_bitscore_by_family(seed_names, seed_points)

    print('calculating centroids for seed clusters..')
    from utils.helpers import space
    seed_centroids = {}
    for fam, points in seed_groups.items():
        seed_centroids[fam] = space.centroid_of(points)

    closest_family = space.ClosestPoint(seed_centroids.values(), seed_centroids.keys())

    splitted_clusters = split_clusters(clusters, C=c)

    if merge:  # whether to do the merging loop
        for round in range(10):
            print('round:', round + 1)

            last_split_clusters = splitted_clusters
            merged_clusters = merge_clusters(closest_family, splitted_clusters)

            if len(merged_clusters) == 1:
                print('unfortunately after merging there is only one cluster left...')
                print('we\'ll assume that the one cluster is the answer')
                splitted_clusters = merged_clusters
                break

            splitted_clusters = split_clusters(merged_clusters, C=c)

            if identical_clusters(last_split_clusters, splitted_clusters):
                break

    return splitted_clusters


def main():
    import utils
    import argparse
    from os.path import join

    parser = argparse.ArgumentParser(usage='further clustering using inter-cluster distance criteria')
    parser.add_argument('--tag', required=True, help='tag')
    parser.add_argument('--alg', required=True, help='task\'s algorithm description')
    parser.add_argument('--c', type=float, default=1.0, help='splitting cluster parameter')
    parser.add_argument('--merge', default=False, action='store_true', help='whether doing the merge loop')
    args = parser.parse_args()

    point_file = join(utils.path.results_path(), 'combined.{}.normalized.bitscore'.format(
        args.tag
    ))
    cluster_file = join(utils.path.results_path(), 'combined.{}.{}.cluster'.format(args.tag, args.alg))

    print('loading score file')
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(point_file)

    print('loading cluster file:', cluster_file)
    clusters = utils.get.get_clusters(cluster_file, point_file)

    final_clusters = run(clusters, seed_names, seed_points, args.c, args.merge)

    print('saving final cluster to file...')
    outfile = join(utils.path.results_path(), 'combined.{}.{}.refined.cluster'.format(args.tag, args.alg))
    utils.save.save_clusters(outfile, final_clusters)
    print('saved!')


if __name__ == '__main__':
    main()
