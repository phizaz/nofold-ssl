def open_result(file):
    import csv
    rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def row_score(row):
    if float(row['max_in_cluster']) < 0.8:
        return 0
    else:
        return 1 * float(row['sensitivity']) + 1 * float(row['precision']) + 1 * float(row['max_in_cluster'])


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
    exacts = ['inc_centroids', 'length_norm', 'alg']
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
        rows = filter(intelligient_filter(col, val), rows)

    return list(rows)


def get_many(cols, row):
    return tuple(row[col] for col in cols)


def open_file_get_only(file, args, vals):
    from os.path import join
    from src import utils
    rows = open_result(file)
    rows = many_filters(args, vals, rows)
    assert len(rows) == 1
    return rows[0]


def main():
    from os.path import join
    from src import utils
    file_embed = join(utils.path.results_path(),
                      'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
    file_plain = join(utils.path.results_path(),
                      'parameter_search.2016-09-06 02:17:39.007583-fam40-plain.csv')

    # rows = open_result(file_embed)
    rows = open_result(file_plain)
    scores = list(map(row_score, rows))
    _mean = mean(scores)
    _std = sd(scores)

    args = ['nn_seed', 'inc_centroids', 'length_norm', 'alg', 'alpha', 'c']

    # nn
    scores = sorted_normalized_col('nn_seed', [1, 7, 13, 19], rows, _mean, _std)
    nn_seed = scores[0][0]
    print('nn_seed:', nn_seed)
    print(scores)

    scores = sorted_normalized_col('inc_centroids', ['True', 'False'], rows, _mean, _std, exact=True)
    inc_centroids = scores[0][0]
    print('inc_centroids:', inc_centroids)
    print(scores)

    scores = sorted_normalized_col('length_norm', ['True', 'False'], rows, _mean, _std, exact=True)
    length_norm = scores[0][0]
    print('length_norm:', length_norm)
    print(scores)

    scores = sorted_normalized_col('alg', ['labelSpreading', 'labelPropagation'], rows, _mean, _std, exact=True)
    alg = scores[0][0]
    print('alg:', alg)
    print(scores)

    scores = sorted_normalized_col('alpha', [
        0.6,
        0.7,
        0.8,
        0.9,
        1.0
    ], rows, _mean, _std)
    alpha = scores[0][0]
    print('alpha:', alpha)
    print(scores)

    scores = sorted_normalized_col('c', [
        1.0,
        1.1,
        1.2,
        1.3,
        1.4,
        1.5
    ], rows, _mean, _std)
    c = scores[0][0]
    print('c:', c)
    print(scores)

    bg_file = join(utils.path.results_path(),
                   'parameter_search.2016-09-06 10:23:00.211147-fam75id-bg.csv')
    row = open_file_get_only(bg_file, args, [
        nn_seed, inc_centroids, length_norm, alg, alpha, c
    ])
    print(get_many(['sensitivity', 'precision', 'max_in_cluster'], row))

    embed_file = join(utils.path.results_path(),
                      'parameter_search.2016-09-04 19:51:43.718908-fam75id-embed.csv')
    row = open_file_get_only(embed_file, args, [
        nn_seed, inc_centroids, length_norm, alg, alpha, c
    ])
    print(get_many(['sensitivity', 'precision', 'max_in_cluster'], row))

    plain_file = join(utils.path.results_path(),
                      'parameter_search.2016-09-06 06:10:32.356377-fam75id-plain.csv')
    row = open_file_get_only(plain_file, args, [
        nn_seed, inc_centroids, length_norm, alg, alpha, c
    ])
    print(get_many(['sensitivity', 'precision', 'max_in_cluster'], row))


if __name__ == '__main__':
    main()
