from __future__ import print_function


def open_result(file):
    import csv
    rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def l1_score(float):
    return 1 - float


def l2_score(float):
    return (1 - float) ** 2


def row_score(row):
    if float(row['sensitivity']) < 0.7 or float(row['precision']) < 0.7 or float(row['max_in_cluster']) < 0.7:
        return 0
    else:
        sense = float(row['sensitivity'])
        prec = float(row['precision'])
        max_in = float(row['max_in_cluster'])
        return 1.0 / (l1_score(sense) + l1_score(prec) + l1_score(max_in))
        # return (1.0 / ((l2_score(sense) + l2_score(prec) + l2_score(max_in)) ** 0.5))


def row_normalized(row, mean, sd):
    return (row_score(row) - mean) / sd


def sd(scores):
    import numpy as np
    return np.std(scores)


def mean(scores):
    import numpy as np
    return np.mean(scores)


def normalize_array(array):
    import scipy.stats
    return scipy.stats.mstats.zscore(array)


def is_close(thing, target, exact=False):
    if exact:
        return thing == target
    else:
        return abs(float(thing) - target) < 0.01


def sum_score_filter(filter, rows):
    s = sum(
        row_score(row)
        for row in rows
        if filter(row)
    )
    return s


def sum_normalized_filter(filter, rows, mean, sd):
    s = sum(
        row_normalized(row, mean, sd)
        for row in rows
        if filter(row)
    )
    return s


def get_filter(col, val, exact=False):
    from functools import partial
    fn = partial(is_close, exact=exact)
    return lambda x: fn(x[col], val)


def intelligient_filter(col, val):
    exacts = ['inc_centroids', 'length_norm', 'alg', 'multilabel', 'merge']
    if col in exacts:
        return get_filter(col, val, True)
    else:
        return get_filter(col, val, False)


def sorted_score_col(col, vals, rows, exact=False):
    scores = [
        (val, sum_score_filter(get_filter(col, val, exact=exact), rows))
        for val in vals
        ]
    scores.sort(key=lambda x: -x[1])
    return scores


def sorted_normalized_col(col, vals, rows, mean, sd, exact=False):
    scores = [
        (val, sum_normalized_filter(get_filter(col, val, exact=exact), rows, mean, sd))
        for val in vals
        ]
    scores.sort(key=lambda x: -x[1])
    return scores


def many_filters(cols, vals, rows):
    for col, val in zip(cols, vals):
        # rows = filter(intelligient_filter(col, val), rows)
        rows = filter(get_filter(col, val, True), rows)

    return list(rows)


def get_cols(cols, row):
    return tuple(row[col] for col in cols)


def open_file_get_only(file, args, vals):
    from os.path import join
    from src import utils
    rows = open_result(file)
    rows = many_filters(args, vals, rows)
    assert len(rows) == 1, 'row `{}` not found'.format(vals)
    return rows[0]


def main():
    from os.path import join
    from src import utils
    file = join(utils.path.results_path(),
                'parameter_search.2016-11-01 10:57:54.220566.csv')

    rows = open_result(file)
    scores = list(map(row_score, rows))
    _mean = mean(scores)
    _std = sd(scores)

    from src import parameter_search
    args = parameter_search.get_all_arguments()

    from collections import defaultdict
    possible_vals = defaultdict(set)
    for row in rows:
        for arg in args:
            val = row[arg]
            possible_vals[arg].add(val)

    best_vals = []
    for arg in args:
        scores = sorted_normalized_col(arg, possible_vals[arg], rows, _mean, _std, exact=True)
        best = scores[0][0]
        best_vals.append(best)
        print('arg `{}` best : {}'.format(arg, best))
        print('scores: ', scores)

    target_files = [
        ('bg_file', 'parameter_search.2016-09-10 17:36:24.557450.csv'),
        ('embed_file', 'parameter_search.2016-09-11 12:59:46.078175.csv'),
        ('plain_file', 'parameter_search.2016-09-11 13:00:08.845259.csv'),
        ('synthetic_file', 'parameter_search.2016-09-11 09:53:50.909419.csv')
    ]

    for name, file_name in target_files:
        full_name = join(utils.path.results_path(), file_name)
        row = open_file_get_only(full_name, args, best_vals)
        print('{}: ', get_cols(['sensitivity', 'precision', 'max_in_cluster'], row))


if __name__ == '__main__':
    main()
