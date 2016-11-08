from __future__ import print_function
import numpy as np


def open_result(file):
    import csv
    rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def dist_l1(errors):
    return np.sum(errors)


def dist_l2(errors):
    # l2 regularizer
    return np.linalg.norm(errors)


def errors_of(arr):
    arr = np.array(arr)
    return np.ones(len(arr)) - arr


def row_error(row, dist_fn):
    if float(row['sensitivity']) < 0.7 or float(row['precision']) < 0.7 or float(row['max_in_cluster']) < 0.7:
        return dist_fn(errors_of([0, 0, 0]))  # equals to dist_fn([1,1,1])
    else:
        sense = float(row['sensitivity'])
        prec = float(row['precision'])
        max_in = float(row['max_in_cluster'])
        return dist_fn(errors_of([sense, prec, max_in]))


def row_error_znormalized(row, mean, sd, dist_fn):
    return (row_error(row, dist_fn=dist_fn) - mean) / sd


def sd(scores):
    import numpy as np
    return np.std(scores)


def mean(scores):
    import numpy as np
    return np.mean(scores)


def is_close(thing, target, exact=False):
    if exact:
        return thing == target
    else:
        return abs(float(thing) - target) < 0.01


def avg_normalized_filter(filter, rows, mean, sd, dist_fn):
    l = [row for row in rows if filter(row)]
    s = sum(
        row_error_znormalized(row, mean, sd, dist_fn=dist_fn)
        for row in l
    )
    return s / len(l)


def get_filter(col, val, exact=False):
    from functools import partial
    fn = partial(is_close, exact=exact)
    return lambda x: fn(x[col], val)


def avg(items):
    return sum(items) / len(items)


def round_zero(item):
    return 0.0 if abs(item - 0) < 1e-10 else item


def col_all_scores(col, vals, rows, mean, sd, dist_fn, exact=False):
    scores = [
        (val,
         round_zero(
             avg_normalized_filter(
                 get_filter(col, val, exact=exact),
                 rows, mean, sd, dist_fn=dist_fn)))
        for val in vals
        ]
    scores.sort(key=lambda x: x[1])
    return scores


def get_rows_filtered(cols, vals, rows):
    for col, val in zip(cols, vals):
        rows = filter(get_filter(col, val, True), rows)

    return list(rows)


def get_cols(cols, row):
    return tuple(row[col] for col in cols)


def open_file_get_only(file, args, vals):
    rows = open_result(file)
    rows = get_rows_filtered(args, vals, rows)
    assert len(rows) == 1, 'row `{}` not found'.format(vals)
    return rows[0]


def analyse(rows, dist_fn):
    from functools import partial
    row_error_partial = partial(row_error, dist_fn=dist_fn)
    scores = list(map(row_error_partial, rows))
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
        scores = col_all_scores(arg, possible_vals[arg], rows, _mean, _std, dist_fn=dist_fn, exact=True)
        best = scores[0][0]
        best_vals.append(best)
        print('arg `{}` best : {}'.format(arg, best))
        print('scores: ', scores)

    return args, best_vals


def apply(args, best_vals, files):
    import utils
    from os.path import join
    for name, file_name in files:
        full_name = join(utils.path.results_path(), file_name)
        row = open_file_get_only(full_name, args, best_vals)
        print('{}: {}'.format(name, get_cols(['sensitivity', 'precision', 'max_in_cluster'], row)))


if __name__ == '__main__':
    import utils
    from os.path import join

    # file = 'parameter_search.2016-11-02 15:01:21.810874.csv'
    file = 'parameter_search.2016-11-07 17:36:39.911944.csv'
    rows = open_result(join(utils.path.results_path(), file))
    args, best_vals = analyse(rows, dist_l2)

    target_files = [
        ('itself', file),
        # ('bg_file', 'parameter_search.2016-09-10 17:36:24.557450.csv'),
        # ('embed_file', 'parameter_search.2016-09-11 12:59:46.078175.csv'),
        # ('plain_file', 'parameter_search.2016-09-11 13:00:08.845259.csv'),
        # ('synthetic_file', 'parameter_search.2016-09-11 09:53:50.909419.csv')
    ]
    apply(args, best_vals, target_files)
