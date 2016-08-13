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

def get_record_count(db_file):
    return len(get_records(db_file))

def get_query_records(query):
    from os.path import join
    from .path import queries_path

    return get_records(join(queries_path(), query, query + '.db'))

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