from __future__ import print_function


def run_combine(query, unformatted, cripple, nn_seed, inc_centroids):
    import combine_rfam_bitscore
    from multiprocessing import cpu_count
    return combine_rfam_bitscore.run(query, unformatted, cripple, nn_seed, inc_centroids, cpu=cpu_count())


def run_normalize(names, points, header, query, pca_n, length_norm):
    import normalize_bitscore
    return normalize_bitscore.run(names, points, header, query, pca_n, length_norm)


def run_clustering(names, points, header, alg, kernel, gamma, alpha, multilabel):
    import clustering
    import utils
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore_plain(names, points,
                                                                                                         header)
    clusters = clustering.run(seed_names, seed_points, query_names, query_points, alg, kernel, alpha, -1, gamma,
                              multilabel)
    return clusters


def run_cluster_refinement(clusters, names, points, header, c, merge):
    import cluster_refinement
    import utils
    seed_names, seed_points, _, _, _ = utils.get.get_seed_query_bitscore_plain(names, points, header)
    clusters = cluster_refinement.run(clusters, seed_names, seed_points, c, merge)
    return clusters


def run_evaluate(name_clusters, names):
    import evaluate
    import utils
    names = filter(lambda x: not utils.short.is_bg(x), names)
    results, average = evaluate.run(names, name_clusters)
    return average


def run_refinement_and_evaluate(clusters, names, points, header, c, merge):
    clusters = run_cluster_refinement(clusters, names, points, header, c, merge)
    name_clusters = [
        cluster.names
        for cluster in clusters
        ]
    import utils
    _, _, query_names, _, _ = utils.get.get_seed_query_bitscore_plain(names, points, header)
    return run_evaluate(name_clusters, query_names)


def save(arguments, results):
    import utils
    from os.path import join
    outfile = join(utils.path.results_path(), 'parameter_search.{}.csv'.format(utils.short.datetime_now()))
    cols = arguments + ['sensitivity', 'precision', 'max_in_cluster']
    rows = [
        key + (val['sensitivity'], val['precision'], val['max_in_cluster'])
        for key, val in results.items()
        ]
    utils.save.save_csv(cols, rows, outfile)
    return cols, rows


def load_search_space_file(file):
    import json
    with open(file) as handle:
        search_space = json.load(handle)
    return search_space


def get_search_arguments():
    search_arguments = [
        'query', 'nn_seed', 'inc_centroids', 'components', 'length_norm', 'alg', 'kernel', 'gamma', 'alpha',
        'multilabel', 'c', 'merge'
    ]
    query_arguments = ['query', 'unformatted', 'cripple']
    return search_arguments, query_arguments


def get_all_arguments():
    search_args, query_args = get_search_arguments()
    return query_args + search_args[1:]  # omit the 'query' argument


def avg_cripple_itr(cripple):
    times = 10
    if cripple == 0:
        yield True
    else:
        for i in range(times):
            yield True


def search_level_combine(space_query, space_nn_seed, space_inc_centroids):
    from itertools import product
    from collections import OrderedDict

    for each in space_query:
        for _ in avg_cripple_itr(
                each['cripple']):  # to run those with 'crippled' many times (and be averaged out afterwards)
            for nn_seed, inc_centroids in product(space_nn_seed, space_inc_centroids):
                print('combining query:{} cripple:{} nn_seed:{}'.format(each['query'], each['cripple'], nn_seed))
                names, points, header = run_combine(each['query'], each['unformatted'], each['cripple'], nn_seed,
                                                    inc_centroids)
                conf = OrderedDict([
                    ('query', each['query']),
                    ('unformatted', each['unformatted']),
                    ('cripple', each['cripple']),
                    ('nn_seed', nn_seed),
                    ('inc_centroids', inc_centroids),
                ])
                yield (conf, (names, points, header))

                names, points, header = None, None, None
                import gc
                gc.collect()


def search_level_normalize(combine_level, space_components, space_length_norm):
    from itertools import product
    for conf, (names, points, header) in combine_level:
        for components, length_norm in product(space_components, space_length_norm):
            print('normalizing query: {} length_norm: {}'.format(conf['query'], length_norm))
            _names, _points, _header = run_normalize(names, points, header, conf['query'], components, length_norm)

            names, points, header = None, None, None
            import gc
            gc.collect()

            conf = conf.copy()
            conf['components'] = components
            conf['length_norm'] = length_norm
            yield (conf, (_names, _points, _header))

            _names, _points, _header = None, None, None
            import gc
            gc.collect()


def search_level_clustering(normalize_level, space_alg, space_kernel, space_gamma, space_alpha, space_multilabel):
    from itertools import product
    for conf, (names, points, header) in normalize_level:
        for alg, kernel, gamma, alpha, multilabel in product(space_alg, space_kernel, space_gamma, space_alpha,
                                                             space_multilabel):
            print(
                'clustering query: {} alg: {} kernel: {} gamma: {} alpha: {} multilabel: {}'.format(conf['query'], alg,
                                                                                                    kernel,
                                                                                                    gamma,
                                                                                                    alpha,
                                                                                                    multilabel))
            clusters = run_clustering(names, points, header, alg, kernel, gamma, alpha, multilabel)
            conf = conf.copy()
            conf['alg'] = alg
            conf['kernel'] = kernel
            conf['gamma'] = gamma
            conf['alpha'] = alpha
            conf['multilabel'] = multilabel
            yield (conf, (names, points, header, clusters))

        names, points, header = None, None, None
        import gc
        gc.collect()


def search_level_refine_eval(clustering_level, space_c, space_merge):
    from itertools import product
    for conf, (names, points, header, clusters) in clustering_level:
        for c, merge in product(space_c, space_merge):
            print('refining query: {} c: {} merg: {} and evaluating ...'.format(conf['query'], c, merge))
            avg = run_refinement_and_evaluate(clusters, names, points, header, c, merge)
            conf = conf.copy()
            conf['c'] = c
            conf['merge'] = merge
            yield (conf, (avg))

        names, points, header, clusters = None, None, None, None
        import gc
        gc.collect()


def avg_results(raw_results):
    # average out results with the same 'idx'
    results = {}
    from operator import itemgetter
    for idx, result_list in raw_results.items():
        keys = ['sensitivity', 'precision', 'max_in_cluster']
        avg_sense, avg_prec, avg_max_in = [
            float(sum(map(itemgetter(key), result_list))) / len(result_list)
            for key in keys
            ]
        results[idx] = dict(zip(keys, (avg_sense, avg_prec, avg_max_in)))

    return results


def get_job_cnt(search_space):
    from src import utils
    search_arguments, query_arguments = get_search_arguments()

    def cnt(search_arg):
        if search_arg == 'query':
            s = 0
            for query in search_space['query']:
                s += utils.short.cardinality(avg_cripple_itr(query['cripple']))
            return s
        else:
            return len(search_space[search_arg])

    total_job_cnt = reduce(lambda a, b: a * b,
                           (cnt(a) for a in search_arguments),
                           1)
    return total_job_cnt


def param_search(search_space):
    search_arguments, query_arguments = get_search_arguments()
    # search space validation
    for arg in search_arguments:
        assert arg in search_space, 'missing arg `{}`'.format(arg)
    for query in search_space['query']:
        for arg in query_arguments:
            assert arg in query, 'missing arg `{}` in query section'.format(arg)

    total_job_cnt = get_job_cnt(search_space)
    print('total jobs cnt: {}'.format(total_job_cnt))

    combine_level = search_level_combine(search_space['query'], search_space['nn_seed'], search_space['inc_centroids'])
    normalize_level = search_level_normalize(combine_level, search_space['components'], search_space['length_norm'])
    clustering_level = search_level_clustering(normalize_level, search_space['alg'], search_space['kernel'],
                                               search_space['gamma'],
                                               search_space['alpha'], search_space['multilabel'])
    eval_level = search_level_refine_eval(clustering_level, search_space['c'], search_space['merge'])

    from collections import defaultdict
    raw_results = defaultdict(list)
    for i, (conf, avg) in enumerate(eval_level, 1):
        idx = tuple(conf.values())
        assert len(idx) == len(get_all_arguments())

        raw_results[idx].append(avg)

        print('({}/{}) done! results sense: {} prec: {} max_in: {}'.format(
            i, total_job_cnt,
            avg['sensitivity'],
            avg['precision'],
            avg['max_in_cluster']
        ))

    return avg_results(raw_results)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
    parser.add_argument('search_space_file', help='a json file of the search space')
    args = parser.parse_args()

    search_space = load_search_space_file(args.search_space_file)
    results = param_search(search_space)

    save(get_all_arguments(), results)


if __name__ == '__main__':
    main()
