from __future__ import print_function

'''
Semi-supervised clustering using label propagation
This will definitely give lesser-than-actual number of clusters, becasue of the insufficient 'seed' families.
'''


def run(seed_names, seed_points, query_names, query_points, alg, kernel, alpha, nn, gamma, multilabel):
    import utils.helpers.namemap

    names = seed_names + query_names
    family_to_int, int_to_family = utils.helpers.namemap.namemap(map(utils.short.general_fam_of, names))

    print('having', len(seed_points) + len(query_points), 'points')

    print('training SSL model...')

    # selecting alg
    from sklearn.semi_supervised import LabelPropagation, LabelSpreading

    if alg == 'labelPropagation':
        print('using labelPropagation')
        ssl_alg = LabelPropagation
    elif alg == 'labelSpreading':
        print('using labelSpreading')
        ssl_alg = LabelSpreading
    else:
        print('wrong alg option')
        sys.exit(1)

    print('using clamping (alpha) of', alpha)

    # selecting options
    if kernel == 'knn':
        print('using KNN kernel')
        print('n_neighbors:', nn)
        ssl = ssl_alg(kernel='knn', n_neighbors=nn, alpha=alpha)
    elif kernel == 'rbf':
        print('using RBF kernel')
        print('gamma:', gamma)
        ssl = ssl_alg(kernel='rbf', gamma=gamma, alpha=alpha)
    else:
        print('wrong kernel option')
        sys.exit()

    X = seed_points + query_points
    seed_labels = list(map(lambda n: family_to_int[n], map(utils.short.fam_of, seed_names)))
    query_labels = [-1 for i in range(len(query_points))]
    Y = seed_labels + query_labels
    ssl.fit(X, Y)

    if multilabel:
        predicted_probs = ssl.label_distributions_[len(seed_points):]
        # print(predicted_probs[:2])

        from src.utils.helpers import lmethod

        clusters_cnt = lmethod.get_clusters_cnt(predicted_probs)
        print('l-method clusters_cnt:', clusters_cnt)

        from sklearn.cluster import AgglomerativeClustering
        agg = AgglomerativeClustering(n_clusters=clusters_cnt, affinity='euclidean', linkage='ward')
        agg.fit(predicted_probs)
        query_predicted_labels = agg.labels_
    else:
        query_predicted_labels = ssl.transduction_[len(seed_points):]

    groups = {}
    for name, label, point in zip(query_names, query_predicted_labels, query_points):
        if label not in groups:
            groups[label] = []
        groups[label].append((name, point))

    from utils.helpers import space
    clusters = []
    for name, points in groups.items():
        clusters.append(space.Cluster(
            names=map(lambda x: x[0], points),
            points=map(lambda x: x[1], points),
        ))

    return clusters


if __name__ == '__main__':
    import argparse
    from os.path import join
    import utils
    import sys

    parser = argparse.ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
    parser.add_argument('--tag', required=True, help='tag')
    parser.add_argument('--alg', default='labelSpreading', help='labelPropagation or labelSpreading ?')
    parser.add_argument('--kernel', default='rbf', help='kernel')
    parser.add_argument('--gamma', type=float, default=0.5, help='rbf kernel\'s gamma')
    parser.add_argument('--nn', type=int, default=19, help='knn\'s nearest neighbor parameter')
    parser.add_argument('--alpha', type=float, help='clamping parameter for SSL model')
    parser.add_argument('--multilabel', default=False, action='store_true',
                        help='whether or not to use l-method to cluster on the label confidence domain, '
                             'instead of using traditional semi-supervised learning')
    args = parser.parse_args()

    file = join(utils.path.results_path(),
                'combined.{}.normalized.bitscore'.format(args.tag))
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(file)

    clusters = run(seed_names, seed_points, query_names, query_points, args.alg, args.kernel, args.alpha, args.nn,
                   args.gamma, args.multilabel)

    outfile = join(utils.path.results_path(), 'combined.{}.{}.cluster'.format(args.tag, args.alg))
    utils.save.save_clusters(outfile, clusters)
    print('saving done!', len(clusters), 'clusters')
