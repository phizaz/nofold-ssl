def check_bitscore(bitscore_file, db_file, strict=True):
    from .path import get_cm_paths
    from .get import get_record_count
    from os.path import exists

    cm_count = len(get_cm_paths())
    record_cnt = get_record_count(db_file)
    if not exists(bitscore_file):
        return False

    with open(bitscore_file, 'r') as handle:
        # ignore the header line
        header = handle.readline()
        col_cnt = len(header.strip().split())

        line_cnt = 0
        for line in handle:
            line = line.strip()

            if len(line) == 0:
                continue

            line_cnt += 1
            tokens = line.split('\t')
            name, scores = tokens[0], tokens[1:]

            if len(scores) != col_cnt:
                return False

            if strict and len(scores) != cm_count:
                return False

        if line_cnt != record_cnt:
            return False
    return True


def check_query(query, strict=True):
    from os.path import join
    from .path import queries_path

    db_file = join(queries_path(), query, query + '.db')
    bitscore_file = join(queries_path(), query, query + '.bitscore')
    return check_bitscore(bitscore_file, db_file, strict=strict)


def check_family(family):
    from os.path import join
    from .path import db_path

    db_file = join(db_path(), family, family + '.db')
    bitscore_file = join(db_path(), family, family + '.bitscore')
    return check_bitscore(bitscore_file, db_file)
