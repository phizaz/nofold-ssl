from __future__ import print_function

def plot_multibars(data, title):
    import numpy as np
    import matplotlib.pyplot as plt
    fig, ax_all = plt.subplots(len(data), 5)
    fig.suptitle(title)

    size = fig.get_size_inches() * 2
    fig.set_size_inches(size[0], size[1])


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

    # plt.show()
    from src import utils
    from os.path import join
    plt.savefig(join(utils.path.results_path(), '{}.png'.format(title)))

if __name__ == '__main__':
    from src import utils
    from os.path import join
    from src.param_analysis import analyse, open_result, get_rows_filtered, dist_l2, dist_l1, get_cols
    print('Param search embed cripple 20 results:')
    file = join(utils.path.results_path(),
                'nofold-ssl-fam40-embed-cripple-20.csv')
    rows = open_result(file)
    # rows = get_rows_filtered([], [], rows)
    args, best_vals = analyse(rows, dist_l2)

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
        "c": [
            1.0,
            1.02,
            1.05,
            1.08,
            1.1,
            1.2,
            1.3
        ],
    }

    default = {
        'nn_seed': '19',
        'cripple': '20',
        'inc_centroids': 'True',
        'length_norm': 'True',
    }

    from itertools import product

    for c in space['c']:
        conf = default.copy()
        conf['c'] = str(c)

        data = []
        for merge, multilabel in product(space['merge'], space['multilabel']):
            dat = []
            data.append((dat, 'mg={}, ml={}'.format(merge, multilabel)))
            for alpha in space['alpha']:
                _, gammas, As, Bs, Cs = row = (alpha, [], [], [], [])
                dat.append(row)
                for gamma in space['gamma']:
                    # some prefixed parameters
                    conf = dict(conf.items() +
                                {
                                    'multilabel': multilabel,
                                    'c': str(c),
                                    'merge': merge,
                                    'gamma': str(gamma),
                                    'alpha': str(alpha)
                                }.items())

                    row = get_rows_filtered(conf.keys(), conf.values(), rows)[0]
                    A, B, C = get_cols(['precision', 'sensitivity', 'max_in_cluster'], row)
                    gammas.append(gamma)
                    As.append(A)
                    Bs.append(B)
                    Cs.append(C)

        # plot to file
        plot_multibars(data, 'fam40 embed cripple 20 c = {}'.format(c))

