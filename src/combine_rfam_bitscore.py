from __future__ import print_function

'''
Combine the rfam seeds with the given query
this should be the first step of doing semi-supervised clustering
'''


def run(query, unformatted, cripple, nn, inc_centroids, cpu=None):
    import utils
    import sys

    # get scores from the query
    query_names, query_points, query_header = utils.get.get_query_bitscores(query)

    all_names = []
    all_points = []

    all_names += query_names
    all_points += query_points
    print('query cols count:', len(query_header))

    available_families = set(utils.get.get_calculated_families())

    if unformatted:
        print('unformatted is "true"')
        print('taking from all we have, dont care for cripples')
        seed_families = available_families
    else:
        query_families = utils.get.get_query_families(query)
        print('families required by the query:', len(query_families))

        not_having_families = query_families - available_families
        print('families we don\'t have:', len(not_having_families))
        print(not_having_families)

        # get some scores from each seeding family (except the marked as crippled)
        cripple_family_count = cripple
        print('cripple count:', cripple_family_count)
        cripple_more = cripple_family_count - len(not_having_families)

        if cripple_more < 0:
            print('cannot attain the target cripple count!')
            sys.exit(1)

        print('more to be crippled:', cripple_more)
        cripple_target_families = query_families - not_having_families
        import random
        cripple_families = random.sample(cripple_target_families, cripple_more)
        print('marked as crippled:', cripple_families)
        seed_families = available_families - set(cripple_families)
        print('taking from:', len(seed_families), '/', len(available_families))

    # taking seeds
    print('always include centroids...')
    print('only closest:', nn, 'neighbors seeds to queries will be taken...')

    seed_points_closest = utils.get.get_knearest_seed_given_query_chunking(nn, query_header, query_points,
                                                                           seed_families,
                                                                           cpu=cpu,
                                                                           chunk_size=100)
    selected_seed = {}
    from collections import Counter
    seed_cnt_by_fam = Counter()
    for each in seed_points_closest:
        for dist, name, point in each:
            if name not in selected_seed:
                family = utils.short.fam_of(name)
                seed_cnt_by_fam[family] += 1
                selected_seed[name] = point
    print('seed count:', len(selected_seed))
    print('seed by family:', seed_cnt_by_fam)

    if inc_centroids:
        # add seed from center of each family
        print('add seeds from a center of each family...')
        for name, point in utils.get.get_families_center_points(seed_families, query_header):
            selected_seed[name] = point
        print('total selected seed count:', len(selected_seed))

    seed_names = []
    seed_points = []
    for name, point in selected_seed.items():
        seed_names.append(name)
        seed_points.append(point)

    all_names += seed_names
    all_points += seed_points
    all_header = query_header
    return all_names, all_points, all_header


if __name__ == '__main__':
    import argparse
    import sys
    import utils

    parser = argparse.ArgumentParser(usage='cluster using semi-supervised label spreading algorithm')
    parser.add_argument('--query', required=True, help='the query name')
    parser.add_argument('--unformatted', default=False, action='store_true',
                        help='is the query from somewhere else? that the name of each query doesn\'t begin with QRF')
    parser.add_argument('--cripple', type=int, help='cripple degree')
    parser.add_argument('--nn', type=int, default=7,
                        help='number of nearest neighbors for closest seed selection')
    parser.add_argument('--inc-centroids', default=False, action='store_true',
                        help='should centroid of each family be included in the seeds ?')
    parser.add_argument('--cpu', type=int, default=None)
    args = parser.parse_args()

    names, points, header = run(query=args.query,
                                unformatted=args.unformatted,
                                cripple=args.cripple,
                                nn=args.nn,
                                inc_centroids=args.inc_centroids,
                                cpu=args.cpu)

    from os.path import join

    # save to file
    if args.unformatted:
        outfile = join(utils.path.results_path(), 'combined.' + args.query + '.bitscore')
    else:
        outfile = join(utils.path.results_path(),
                       'combined.' + args.query + '.cripple' + str(args.cripple) + '.bitscore')
    utils.save.save_bitscores(outfile, names, points, header)

    print('total database size:', len(points))
