if __name__ == '__main__':
    from os.path import join
    from src.param_analysis import *
    from src import utils

    file = 'parameter_search.2016-11-07 17:36:39.911944.csv'
    rows = open_result(join(utils.path.results_path(), file))

    # filter rows
    # rows = get_rows_filtered(['cripple'], ['6'], rows) # 0.4 is overall not bad

    args, best_vals = analyse(rows, dist_l2)

    target_files = [
        ('itself', file),
    ]
    apply(args, best_vals, target_files)