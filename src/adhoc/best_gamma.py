from __future__ import print_function

if __name__ == '__main__':
    from src import utils
    from os.path import join
    from src.param_analysis import analyse, open_result, get_rows_filtered, dist_l2
    print('Param search on pca\' components results:')
    file = join(utils.path.results_path(),
                'parameter_search.2016-11-03 09:08:52.971411.csv')
    rows = open_result(file)
    rows = get_rows_filtered(['query', 'cripple'], ['fam40_typedistributed_plain+bg_weak', '20'], rows)
    args, best_vals = analyse(rows, dist_l2)

    d = dict(zip(args, best_vals))
    print('best gamma:', d['gamma'])
    best_row = get_rows_filtered(args, best_vals, rows)
    print('best row:', best_row)
