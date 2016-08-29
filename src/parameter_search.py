from __future__ import print_function


def run_combine(query, unformatted, cripple, nn_seed, inc_centroids):
    from combine_rfam_bitscore import run
    return run(query, unformatted, cripple, nn_seed, inc_centroids)


def run_normalize(names, points, header, query, length_norm):
    from normalize_bitscore import run
    return run(names, points, header, query, 100, length_norm)


def run_clustering(names, points, header, alg, kernel, gamma, alpha):
    from clustering import run
    import utils
    seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore_plain(names, points,
                                                                                                         header)
    clusters = run(seed_names, seed_points, query_names, query_points, alg, kernel, alpha, -1, gamma)
    return clusters


def run_cluster_refinement(clusters, names, points, header, c):
    from cluster_refinement import run
    import utils
    seed_names, seed_points, _, _, _ = utils.get.get_seed_query_bitscore_plain(names, points, header)
    clusters = run(clusters, seed_names, seed_points, c)
    return clusters


def run_evaluate(name_clusters, names):
    from evaluate import run
    import utils
    names = filter(lambda x: not utils.short.is_bg(x), names)
    results, average = run(names, name_clusters)
    return average


def run_refinement_and_evaluate(clusters, names, points, header, c):
    clusters = run_cluster_refinement(clusters, names, points, header, c)
    name_clusters = [
        cluster.names
        for cluster in clusters
        ]
    import utils
    _, _, query_names, _, _ = utils.get.get_seed_query_bitscore_plain(names, points, header)
    return run_evaluate(name_clusters, query_names)


def save(search_arguments, results):
    import utils
    from os.path import join
    outfile = join(utils.path.results_path(), 'parameter_search.{}.csv'.format(utils.short.datetime_now()))
    cols = search_arguments + ['sensitivity', 'precision', 'max_in_cluster']
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


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(usage='cluster using semi-supervised label propagation algorithm')
    parser.add_argument('search_space_file', help='a json file of the search space')
    args = parser.parse_args()

    search_arguments = [
        'query', 'unformatted', 'cripple', 'nn_seed', 'inc_centroids', 'length_norm', 'alg', 'kernel', 'gamma', 'alpha',
        'c'
    ]

    search_space = load_search_space_file(args.search_space_file)

    assert len(search_space['query']) == len(search_space['unformatted']) == len(search_space['cripple'])

    from itertools import product

    results = {}

    for query, unformatted, cripple in zip(search_space['query'], search_space['unformatted'], search_space['cripple']):
        for nn_seed, inc_centroids in product(search_space['nn_seed'], search_space['inc_centroids']):
            print('combining query:{} cripple:{} nn_seed:{}'.format(query, cripple, nn_seed))
            names, points, header = run_combine(query, unformatted, cripple, nn_seed, inc_centroids)

            for length_norm in search_space['length_norm']:
                print('normalizing query: {} length_norm: {}'.format(query, length_norm))
                names, points, header = run_normalize(names, points, header, query, length_norm)

                for alg, kernel, gamma, alpha in product(
                        search_space['alg'],
                        search_space['kernel'],
                        search_space['gamma'],
                        search_space['alpha']
                ):
                    print(
                        'clustering query: {} alg: {} kernel: {} gamma: {} alpha: {}'.format(query, alg, kernel, gamma,
                                                                                             alpha))
                    clusters = run_clustering(names, points, header, alg, kernel, gamma, alpha)

                    for c in search_space['c']:
                        print('refining query: {} c: {} and evaluating ...'.format(query, c))
                        avg = run_refinement_and_evaluate(clusters, names, points, header, c)

                        idx = (
                            query, unformatted, cripple, nn_seed, inc_centroids, length_norm, alg, kernel, gamma, alpha,
                            c
                        )
                        assert len(idx) == len(search_arguments)

                        results[idx] = avg

                        print('results sense: {} prec: {} max_in: {}'.format(
                            avg['sensitivity'],
                            avg['precision'],
                            avg['max_in_cluster']
                        ))

    save(search_arguments, results)
