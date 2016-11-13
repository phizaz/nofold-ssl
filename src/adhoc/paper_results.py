if __name__ == '__main__':
    from src import utils
    from os.path import join

    file = join(utils.path.results_path(), 'nofold-ssl-paper-results.csv')
    from src.param_analysis import *

    rows = open_result(file)

    queries = ['rfam75id_dinuc3000-rename',
               'rfam75id_embed-rename',
               'rfam75id-rename',
               'novel-1-2-3hp']

    print('Nofold SSL Results on Nofold\'s paper datasets')
    for query in queries:
        params = {
            'query': query,
            'gamma': '0.3',
            'alpha': '0.7',
            'c': '1.1'
        }

        _rows = get_rows_filtered(params.keys(),
                                  params.values(),
                                  rows)

        prec, sense, max_in = get_cols(['precision', 'sensitivity', 'max_in_cluster'], _rows[0])

        print('{} : {}, {}, {}'.format(query, sense, prec, max_in))
