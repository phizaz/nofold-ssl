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
    pc_header = ['PC{}'.format(i+1) for i in range(components)]
    from sklearn.decomposition import PCA
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

if __name__ == '__main__':
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
    file_ext = ''

    if args.lengthnorm:
        print('Length normalizing ...')
        points = length_normalize(names, points, header, args.query)
        file_ext += '.zNorm'
        file = join(utils.path.results_path(), '{}{}.bitscore'.format(no_extension_name, file_ext))
        utils.save.save_bitscores(file, names, points, header)
        print('Saved length normalize ...')

    print('PCA {} components ..'.format(args.components))
    points, pc_header = pca(args.components, points)
    file_ext += '.pcNorm{}'.format(args.components)
    file = join(utils.path.results_path(), '{}{}.bitscore'.format(no_extension_name, file_ext))
    utils.save.save_bitscores(file, names, points, pc_header)
    print('Saved PCA normalize')


    print('Z-normalizing ..')
    points = znormalize(points)
    file_ext += '.zNorm'
    file = join(utils.path.results_path(), '{}{}.bitscore'.format(no_extension_name, file_ext))
    utils.save.save_bitscores(file, names, points, pc_header)
    print('Saved Z-normalize ...')

