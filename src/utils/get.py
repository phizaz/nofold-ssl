from __future__ import print_function

def get_all_families():
    from .path import db_path
    from os import listdir
    from os.path import isdir, join

    path = db_path()
    families = [f for f in listdir(path) if isdir(join(path, f))]
    return families


def get_calculated_families():
    from multiprocessing import Pool
    from .check import check_family

    families = get_all_families()
    pool = Pool()
    check_results = pool.map(check_family, families)
    pool.close()
    available_families = sorted(map(lambda fr: fr[0], filter(lambda fr: fr[1], zip(families, check_results))))
    return available_families


def get_records(db_file):
    from Bio import SeqIO

    with open(db_file, 'r') as handle:
        records = list(SeqIO.parse(handle, 'fasta'))
    return records


def get_sequences(db_file):
    records = get_records(db_file)
    return list(map(lambda x: str(x.seq), records))


def get_record_count(db_file):
    return len(get_records(db_file))


def get_query_records(query):
    from os.path import join
    from .path import queries_path

    return get_records(join(queries_path(), query, query + '.db'))


def get_query_sequences(query):
    records = get_query_records(query)
    return list(map(lambda x: str(x.seq), records))


def get_query_families(query):
    from .short import is_bg, qfam_of

    families = set()
    for record in get_query_records(query):
        if is_bg(record.name): continue
        fam = qfam_of(record.name)
        families.add(fam)
    return families


def get_bitscores(bitscore_file):
    with open(bitscore_file, 'r') as handle:
        names = []
        points = []
        header = handle.readline().strip().split()
        for line in handle:
            tokens = line.strip().split()
            name, scores = tokens[0], list(map(float, tokens[1:]))
            assert len(scores) == len(header)
            names.append(name)
            points.append(scores)
    return names, points, header


def get_query_bitscores(query):
    from os.path import join
    from .path import queries_path

    return get_bitscores(join(queries_path(), query, query + '.bitscore'))


def get_family_bitscores(family):
    from os.path import join
    from .path import db_path

    return get_bitscores(join(db_path(), family, family + '.bitscore'))


def get_family_sequences(family):
    from os.path import join
    from .path import db_path

    return get_sequences(join(db_path(), family, family + '.db'))


def get_family_header_string(family):
    from os.path import join
    from .path import db_path
    file = join(db_path(), family, family + '.bitscore')
    with open(file, 'r') as handle:
        header = handle.readline().strip()
    return header


def get_family_header(family):
    from os.path import join
    from .path import db_path
    file = join(db_path(), family, family + '.bitscore')
    with open(file, 'r') as handle:
        header = handle.readline().strip().split()
    return header

def get_knearest_points_given_a(k, a_points, target_names, target_points):
    from sklearn.neighbors import BallTree
    k = min(k, len(target_points))
    tree = BallTree(target_points)
    dists, idxs = tree.query(a_points, k=k)

    results = [[] for i in range(len(a_points))]
    for idx, (_dists, _idxs) in enumerate(zip(dists, idxs)):
        names = list(map(lambda idx: target_names[idx], _idxs))
        points = list(map(lambda idx: target_points[idx], _idxs))
        results[idx] += list(zip(_dists, names, points))
    return results

def get_knearest_seed_in_family_given_query(k, query_header, query_points, family):
    from .modify import retain_bitscore_cols
    seed_names, seed_points, seed_header = get_family_bitscores(family)
    seed_points, seed_header = retain_bitscore_cols(query_header, seed_points, seed_header)
    return get_knearest_points_given_a(k, query_points, seed_names, seed_points)

def get_knearest_seed_given_query(k, query_header, query_points, families=None):
    if not families:
        print('retriving calculated families...')
        families = get_calculated_families()

    from sklearn.neighbors import BallTree
    from multiprocessing import Pool, cpu_count
    from functools import partial
    pool = Pool(cpu_count())

    results = [[] for i in range(len(query_points))]

    def clean_up():
        from operator import itemgetter
        for each in results:
            each.sort(key=itemgetter(0))
            del each[k:]

    fn = partial(get_knearest_seed_in_family_given_query, k, query_header, query_points)
    for i, each in enumerate(pool.imap_unordered(fn, families)):
        print('family:', i, 'of', len(families))
        for all, local in zip(results, each):
            all += local

        if i % 100 == 0:
            print('cleaning up ...')
            clean_up()

    clean_up()
    pool.close()

    return results
