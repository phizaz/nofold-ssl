from __future__ import print_function
import logging

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
    return query_args + search_args[1:] # omit the 'query' argument


def param_search(search_space):
    search_arguments, query_arguments = get_search_arguments()
    # search space validation
    for arg in search_arguments:
        assert arg in search_space, 'missing arg `{}`'.format(arg)
    for query in search_space['query']:
        for arg in query_arguments:
            assert arg in query, 'missing arg `{}` in query section'.format(arg)

    total_job_cnt = reduce(lambda a, b: a * b,
                           (len(search_space[a]) for a in search_arguments),
                           1)
    print('total jobs cnt: {}'.format(total_job_cnt))

    import itertools
    job_no = itertools.count(1)
    results = {}
    from itertools import product
    for each in search_space['query']:
        query, unformatted, cripple = A = each['query'], each['unformatted'], each['cripple']

        for B in product(search_space['nn_seed'], search_space['inc_centroids']):
            nn_seed, inc_centroids = B

            print('combining query:{} cripple:{} nn_seed:{}'.format(query, cripple, nn_seed))
            c_names, c_points, c_header = run_combine(query, unformatted, cripple, nn_seed, inc_centroids)

            for C in product(search_space['components'], search_space['length_norm']):
                components, length_norm = C

                print('normalizing query: {} length_norm: {}'.format(query, length_norm))
                n_names, n_points, n_header = run_normalize(c_names, c_points, c_header, query, components, length_norm)

                for D in product(
                        search_space['alg'],
                        search_space['kernel'],
                        search_space['gamma'],
                        search_space['alpha'],
                        search_space['multilabel'],
                ):
                    alg, kernel, gamma, alpha, multilabel = D

                    print(
                        'clustering query: {} alg: {} kernel: {} gamma: {} alpha: {} multilabel: {}'.format(query, alg,
                                                                                                            kernel,
                                                                                                            gamma,
                                                                                                            alpha,
                                                                                                            multilabel))
                    clusters = run_clustering(n_names, n_points, n_header, alg, kernel, gamma, alpha, multilabel)

                    for E in product(search_space['c'], search_space['merge']):
                        c, merge = E

                        print('refining query: {} c: {} merg: {} and evaluating ...'.format(query, c, merge))
                        avg = run_refinement_and_evaluate(clusters, n_names, n_points, n_header, c, merge)

                        idx = tuple(
                            item
                            for l in (A, B, C, D, E)
                            for item in l
                        )
                        assert len(idx) == len(get_all_arguments())

                        results[idx] = avg

                        print('({}/{}) done! results sense: {} prec: {} max_in: {}'.format(
                            job_no.next(), total_job_cnt,
                            avg['sensitivity'],
                            avg['precision'],
                            avg['max_in_cluster']
                        ))

    return results


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
    parser.add_argument('search_space_file', help='a json file of the search space')
    args = parser.parse_args()

    search_space = load_search_space_file(args.search_space_file)
    results = param_search(search_space)

    save(get_all_arguments(), results)
