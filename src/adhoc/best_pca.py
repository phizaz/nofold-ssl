from __future__ import print_function

if __name__ == '__main__':
    from src import utils
    from os.path import join
    from src.param_analysis import analyse, open_result
    print('Param search on pca\' components results:')
    file = join(utils.path.results_path(),
                'nofold-ssl-fam40-pca.csv')
    rows = open_result(file)
    args, best_vals = analyse(rows)

    d = dict(zip(args, best_vals))
    print('best pca components count: ', d['components'])
