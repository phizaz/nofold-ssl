from __future__ import print_function

'''
Showing the scores varying on gamma and alpha for fam40-plain dataset
'''


def plot_multibars(data, title):
    import numpy as np
    import matplotlib.pyplot as plt
    fig, ax_all = plt.subplots(len(data), 5)
    fig.suptitle(title)

    for dat, ax_row in zip(data, ax_all):
        row, subtitle = dat
        for ax, (alpha, gammas, As, Bs, Cs) in zip(ax_row, row):
            ind = np.arange(len(gammas))
            width = 0.25

            ax.bar(ind, As, width, color='r')
            ax.bar(ind + width, Bs, width, color='g')
            ax.bar(ind + 2 * width, Cs, width, color='b')

            ax.set_ylabel(subtitle)
            ax.set_title('alpha = {}'.format(alpha))
            ax.set_xticks(ind + width)
            ax.set_xticklabels(gammas)
            ax.set_ylim((0, 1.0))

    plt.show()

    # from src import utils
    # from os.path import join
    # plt.savefig(join(utils.path.results_path(), '{}.png'.format(title)))


if __name__ == '__main__':
    from os.path import join
    from src.param_analysis import *
    from src import utils

    file = 'nofold-ssl-fam40-plain-cripple-20.csv'
    rows = open_result(join(utils.path.results_path(), file))

    space = {
        'inc_centroids': ['True'],
        'length_norm': ['True'],
        'merge': ['True', 'False'],
        'multilabel': ['True', 'False'],
        'cripple': ['20'],
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

    data = []
    for merge, multilabel in product(space['merge'], space['multilabel']):
        dat = []
        data.append((dat, 'mg={}, ml={}'.format(merge, multilabel)))
        for alpha in space['alpha']:
            _, gammas, As, Bs, Cs = row = (alpha, [], [], [], [])
            dat.append(row)
            for gamma in space['gamma']:
                # some prefixed parameters
                d = {
                    'nn_seed': '19',
                    'cripple': '20',
                    'inc_centroids': 'True',
                    'length_norm': 'True',
                    'multilabel': multilabel,
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
    plot_multibars(data, 'fam40 plain cripple 20')
