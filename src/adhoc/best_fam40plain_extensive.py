from __future__ import print_function

'''
Showing the scores varying on gamma and alpha for fam40-plain dataset
'''

def plot_multibars(data, title):
    import numpy as np
    import matplotlib.pyplot as plt
    fig, ax_all = plt.subplots(3, 5)
    fig.suptitle(title)

    for dat, ax_row in zip(data, ax_all):
        for ax, (alpha, gammas, As, Bs, Cs) in zip(ax_row, dat):
            ind = np.arange(len(gammas))
            width = 0.25

            ax.bar(ind, As, width, color='r')
            ax.bar(ind + width, Bs, width, color='g')
            ax.bar(ind + 2 * width, Cs, width, color='b')

            ax.set_ylabel('acc')
            ax.set_title('alpha = {}'.format(alpha))
            ax.set_xticks(ind + width)
            ax.set_xticklabels(gammas)
            ax.set_ylim((0, 1.0))

    # plt.show()

    from src import utils
    from os.path import join
    plt.savefig(join(utils.path.results_path(), '{}.png'.format(title)))


if __name__ == '__main__':
    from os.path import join
    from src.param_analysis import *
    from src import utils

    file = 'nofold-ssl-fam40plain-extensive.csv'
    rows = open_result(join(utils.path.results_path(), file))

    # filter rows
    # itself: ('0.83899999999999997', '0.89809323104468297', '0.88')
    # rows = get_rows_filtered(['nn_seed', 'cripple', 'gamma', 'alpha', 'multilabel', 'c', 'inc_centroids', 'length_norm'],
    #                          ['19', '40', '0.5', '1.0', 'True', '1.1', 'False', 'False'],
    #                          rows)  # 0.4 is overall not bad

    space = {
        'inc_centroids': ['True', 'False'],
        'length_norm': ['True', 'False'],
        'merge': ['True', 'False'],
        'cripple': ['6', '20', '40'],
        "gamma": [
            0.3, 0.4, 0.5, 0.6, 0.7
        ],
        "alpha": [
            0.6,
            0.7,
            0.8,
            0.9,
            1.0
        ],
    }

    from itertools import product

    for inc_centroids, length_norm, merge in product(space['inc_centroids'], space['length_norm'], space['merge']):
        data = []
        for cripple in space['cripple']:
            dat = []
            data.append(dat)
            for alpha in space['alpha']:
                _, gammas, As, Bs, Cs = row = (alpha, [], [], [], [])
                dat.append(row)
                for gamma in space['gamma']:
                    # some prefixed parameters
                    d = {
                        'nn_seed': '19',
                        'cripple': cripple,
                        'inc_centroids': inc_centroids,
                        'length_norm': length_norm,
                        'multilabel': 'True',
                        'c': '1.1',
                        'merge': merge,
                        'gamma': str(gamma),
                        'alpha': str(alpha)
                    }
                    row = get_rows_filtered(d.keys(), d.values(), rows)[0]
                    A, B, C = get_cols(['precision', 'sensitivity', 'max_in_cluster'], row)
                    gammas.append(gamma)
                    As.append(A)
                    Bs.append(B)
                    Cs.append(C)

        # plot to file
        plot_multibars(data,
                       ', '.join([
                           '{} = {}'.format(a, b)
                           for a, b in zip(
                               ['inc_centroids', 'length_norm', 'merge'],
                               [inc_centroids, length_norm, merge]
                           )
                       ]))

