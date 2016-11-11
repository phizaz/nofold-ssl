from __future__ import print_function

if __name__ == '__main__':
    from src import utils
    from os.path import join
    from src.param_analysis import analyse, open_result, get_rows_filtered, dist_l2
    print('Param search on gamma results:')
    file = join(utils.path.results_path(),
                'nofold-ssl-fam40-gamma.csv')
    rows = open_result(file)
    rows = get_rows_filtered(['query', 'cripple'], ['fam40_typedistributed_plain+bg_weak', '20'], rows)
    args, best_vals = analyse(rows, dist_l2)

    d = dict(zip(args, best_vals))
    print('best gamma:', d['gamma'])
    best_row = get_rows_filtered(args, best_vals, rows)
    print('best row:', best_row)
