from __future__ import print_function

'''
Normalize the combined bitscore using PCA and Z-normalizer
'''


def length_normalize(names, points, header, query):
    from utils.helpers.lengthnorm import LengthNormalizer
    normalizer = LengthNormalizer()
    n_points = normalizer.length_normalize_full(names, points, header, query)
    return n_points


def pca(components, points):
    assert components <= len(points[0]), 'number of components is more than the actual dimension'
    assert components <= len(points), 'number of components is more than the number of points'
    from sklearn.decomposition import PCA
    pc_header = ['PC{}'.format(i + 1) for i in range(components)]
    pca = PCA(n_components=components)
    pc_points = pca.fit_transform(points)
    return pc_points, pc_header


def znormalize(points):
    import numpy as np
    import utils
    n_points = []
    for col in points.T:
        n_points.append(utils.short.normalize_array(col))
    n_points = np.array(n_points).T
    return n_points


def run(names, points, header, query, components, lengthnorm):
    if lengthnorm:
        print('Length normalizing ...')
        points = length_normalize(names, points, header, query)

    print('PCA {} components ..'.format(components))
    points, header = pca(components, points)

    print('Z-normalizing ..')
    points = znormalize(points)
    return names, points, header


def main():
    import utils
    import argparse
    from os.path import join

    parser = argparse.ArgumentParser(usage='further clustering using inter-cluster distance criteria')
    parser.add_argument('--tag', required=True, help="tag")
    parser.add_argument('--query', required=True, help='query file in the form of db file')
    parser.add_argument('--lengthnorm', default=False, action='store_true', help='whether to use length normalization?')
    parser.add_argument('--components', type=int, default=100, help="PCA's number of components")
    args = parser.parse_args()

    file_name = 'combined.' + args.tag + '.bitscore'
    no_extension_name = '.'.join(file_name.split('.')[:-1])
    print('no_extension_name:', no_extension_name)
    file = join(utils.path.results_path(), file_name)

    names, points, header = utils.get.get_bitscores(file)
    names, points, header = run(names, points, header, args.query, args.components, args.lengthnorm)

    print('Saving results to file...')
    outfile = join(utils.path.results_path(), 'combined.{}.normalized.bitscore'.format(args.tag))
    utils.save.save_bitscores(outfile, names, points, header)
    print('Saving done !')


if __name__ == '__main__':
    main()
