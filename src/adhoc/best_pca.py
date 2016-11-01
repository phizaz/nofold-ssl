if __name__ == '__main__':
    from src import utils
    from os.path import join
    from src.param_analysis import analyse
    print('Param search on pca\' components results:')
    file = join(utils.path.results_path(),
                'parameter_search.2016-11-01 10:57:54.220566.csv')
    args, best_vals = analyse(file)