from __future__ import print_function

'''
Semi-supervised clustering using label propagation
This will definitely give lesser-than-actual number of clusters, becasue of the insufficient 'seed' families.
'''


def run(seed_names, seed_points, query_names, query_points, alg, kernel, alpha, nn, gamma):
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
    query_predicted_labels = ssl.transduction_[len(seed_points):]

    clusters = {}
    for name, label in zip(query_names, query_predicted_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(name)
    return clusters


if __name__ == '__main__':
    import argparse
    from os.path import join
    import utils
    import sys

    parser = argparse.ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
    parser.add_argument('--tag', required=True, help='tag')
    parser.add_argument('--lengthnorm', default=False, action='store_true',
                        help='did you use --lengthnorm in the normalization step')
    parser.add_argument('--alg', default='labelSpreading', help='labelPropagation or labelSpreading ?')
    parser.add_argument('--kernel', default='rbf', help='kernel')
    parser.add_argument('--gamma', type=float, default=0.5, help='rbf kernel\'s gamma')
    parser.add_argument('--nn', type=int, default=19, help='knn\'s nearest neighbor parameter')
    parser.add_argument('--alpha', type=float, help='clamping parameter for SSL model')
    parser.add_argument('--components', type=int, default=100, help='PCA\'s number of components')
    args = parser.parse_args()

    file = join(utils.path.results_path(),
                'combined.{}{}.pcNorm{}.zNorm.bitscore'.format(args.tag, '.zNorm' if args.lengthnorm else '', args.components))
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(file)

    clusters = run(seed_names, seed_points, query_names, query_points, args.alg, args.kernel, args.alpha, args.nn,
                   args.gamma)

    outfile = join(utils.path.results_path(), 'combined.{}.{}.cluster'.format(args.tag, args.alg))
    utils.save.save_name_clusters(outfile, clusters)
    print('saving done!', len(clusters), 'clusters')
