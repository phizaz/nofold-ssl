from __future__ import division, print_function

'''
Evaluate the clustering quality using three benchmarks
1. Sensitivity
2. Precision
3. Max in cluster - how good the sequences of a family are distributed in one big cluster.
'''


def dominator_of(cluster):
    from collections import Counter
    counter = Counter()
    import utils
    for name in cluster:
        fam = utils.short.general_fam_of(name)
        counter[fam] += 1
    dominant_family, cnt = counter.most_common(1).pop()
    return dominant_family, cnt


def sensitivity_of(family, clusters, names_by_family):
    dominating_cnt = 0
    for cluster in clusters:
        dominator, cnt = dominator_of(cluster)
        if dominator == family:
            dominating_cnt += cnt

    all_cnt = len(names_by_family[family])
    return dominating_cnt / all_cnt


def precision_of(family, clusters):
    dominating_cnt = 0
    all_cnt = 0
    for cluster in clusters:
        dominator, cnt = dominator_of(cluster)
        if dominator == family:
            dominating_cnt += cnt
            all_cnt += len(cluster)
    if all_cnt == 0:
        return 0
    return dominating_cnt / all_cnt


def family_cnt_in_cluster(family, cluster):
    import utils
    cnt = 0
    for name in cluster:
        fam = utils.short.general_fam_of(name)
        if fam == family: cnt += 1
    return cnt


def max_in_cluster_of(family, clusters, names_by_family):
    cnt = max(family_cnt_in_cluster(family, cluster) for cluster in clusters)
    all_cnt = len(names_by_family[family])
    return cnt / all_cnt


def run(names, clusters):
    import utils
    names_by_family = utils.modify.group_names_by_family(names)
    print('number of families:', len(names_by_family))

    families = names_by_family.keys()

    from collections import OrderedDict
    res = OrderedDict()
    res['family'] = []
    res['sensitivity'] = []
    res['precision'] = []
    res['max_in_cluster'] = []
    res['seq_cnt'] = []

    for family in sorted(families):
        res['family'].append(family)
        res['sensitivity'].append(sensitivity_of(family, clusters, names_by_family)),
        res['precision'].append(precision_of(family, clusters)),
        res['max_in_cluster'].append(max_in_cluster_of(family, clusters, names_by_family)),
        res['seq_cnt'].append(len(names_by_family[family]))

    avg = OrderedDict()
    import numpy as np
    weights = res['seq_cnt']
    avg['sensitivity'] = np.average(res['sensitivity'], weights=weights)
    avg['precision'] = np.average(res['precision'], weights=weights)
    avg['max_in_cluster'] = np.average(res['max_in_cluster'], weights=weights)

    return res, avg

def nofold_get_name_clusters(cluster_file):
    print('transforming nofold result ...')
    clusters = []
    with open(cluster_file) as handle:
        handle.readline()
        for line in handle:
            tokens = line.strip().split('\t')
            names = tokens[4].strip().split(',')
            clusters.append(names)
    return clusters

if __name__ == '__main__':
    import argparse
    import utils
    from os.path import join

    parser = argparse.ArgumentParser(usage='evaluate the clustering results')
    parser.add_argument('--file', required=True, help='cluster result file')
    parser.add_argument('--query', required=True, help='query name')
    parser.add_argument('--nofold', action='store_true', default=False, help='is the result from original NoFold ?')
    args = parser.parse_args()

    if args.nofold:
        clusters = nofold_get_name_clusters(args.file)
    else:
        clusters = utils.get.get_name_clusters(args.file)

    print('number of sequences:', sum(len(names) for names in clusters))
    print('number of clusters:', len(clusters))

    names = [
        rec.name
        for rec in utils.get.get_query_records(args.query)
        if not utils.short.is_bg(rec.name)
        ]

    results, average = run(names, clusters)

    output_file = args.file + '.evaluation'
    with open(output_file, 'w') as handle:
        handle.write('\t'.join(results.keys()) + '\n')

        for cols in zip(*results.values()):
            handle.write('\t'.join(map(str, cols)) + '\n')

        handle.write('\t'.join(map(lambda x: 'avg_' + x, average.keys())) + '\n')
        handle.write('\t'.join(map(str, average.values())) + '\n')

    print('done!')
