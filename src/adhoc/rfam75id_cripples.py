'''
Show the effect of cripples on rfam75id-plain dataset
'''

if __name__ == '__main__':
    from src import utils
    from os.path import join

    # file = join(utils.path.results_path(), 'nofold-ssl-rfam75id-plain-cripple.csv')
    # file = join(utils.path.results_path(), 'nofold-ssl-rfam75id-plain-cripple-2.csv')
    file = join(utils.path.results_path(), 'nofold-ssl-rfam75id-plain-cripple-3.csv')
    from src.param_analysis import *

    rows = open_result(file)

    print('Nofold SSL Results on Nofold\'s paper datasets')

    all_sense = []
    all_prec = []
    all_max_in = []
    cripples = range(1, 20 + 1)
    # cripples = [10, 20]

    params = {
        'query': 'rfam75id-rename',
        # 'gamma': '0.3',
        'gamma': '0.3',
        'alpha': '0.7',
        # 'c': '1.1'
        'c': '1.05',
        'multilabel': 'True',
        'merge': 'True'
    }

    for cripple in cripples:
        args = params.copy()
        args['cripple'] = str(cripple)

        _rows = get_rows_filtered(args.keys(),
                                  args.values(),
                                  rows)

        assert len(_rows) == 1

        sense, prec, max_in = get_cols(['sensitivity', 'precision', 'max_in_cluster'], _rows[0])
        all_sense.append(sense)
        all_prec.append(prec)
        all_max_in.append(max_in)

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1)

    fig.suptitle(
        ','.join(
            '{}={}'.format(a, b)
            for a, b in params.items()
        )
    )

    for ax, vals, title in zip(axes, [all_sense, all_prec, all_max_in], ['sense', 'prec', 'max_in']):
        ind = np.arange(len(vals))
        width = 0.25

        ax.bar(ind, vals, width, color='r')

        ax.set_ylabel('score')
        ax.set_title(title)
        ax.set_xticks(ind + width)
        ax.set_xticklabels(cripples)
        ax.set_ylim((0, 1.0))

    plt.show()




