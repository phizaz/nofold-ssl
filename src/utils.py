from os.path import join, isdir, exists
from os import listdir, makedirs
from Bio import SeqIO
from multiprocessing.pool import Pool

path = '../Rfam-seed/db'

def make_path(path):
    if not exists(path):
        makedirs(path)

def get_record_count(db_file):
    with open(db_file, 'r') as handle:
        records = SeqIO.parse(handle, 'fasta')
        names = set(map(lambda x: x.name, records))
        record_cnt = len(names)
    return record_cnt

def get_cm_paths():
    path = join('../models', 'rfam_cms')
    models = filter(lambda x: 'cm' in x, listdir(path))
    full_path = map(lambda x: join(path, x), models)
    return list(full_path)

def is_bg(name):
    bg_keywords = ['dinucShuff', 'bg']
    return any(keyword in name for keyword in bg_keywords)

def fam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'RF':
        raise ValueError('not a seed sequenec, not RF')
    return fam

def qfam_of(name):
    fam = name.split('_')[0]
    if fam[:2] != 'QR':
        raise ValueError('not a query sequence, not QRF')
    # return the family part not including 'Q'
    return fam[1:]

def check_bitscore(bitscore_file, db_file):
    cm_count = len(get_cm_paths())
    record_cnt = get_record_count(db_file)
    if not exists(bitscore_file):
        return False
    with open(bitscore_file, 'r') as handle:
        # ignore the header line
        handle.readline()
        line_cnt = 0
        for line in handle:
            line = line.strip()

            if len(line) == 0:
                continue

            line_cnt += 1
            tokens = line.split('\t')
            name, scores = tokens[0], tokens[1:]
            if len(scores) != cm_count:
                return False

        if line_cnt != record_cnt:
            return False
    return True

def check_query(query):
    db_file = join('../queries', query, query + '.db')
    bitscore_file = join('../queries', query, query + '.bitscore')
    return check_bitscore(bitscore_file, db_file)

def check_family(family):
    db_file = join(path, family, family + '.db')
    bitscore_file = join(path, family, family + '.bitscore')
    return check_bitscore(bitscore_file, db_file)

def get_all_families():
    families = [f for f in listdir(path) if isdir(join(path, f))]
    return families

def get_calculated_families():
    families = get_all_families()
    pool = Pool()
    check_results = pool.map(check_family, families)
    pool.close()
    available_families = sorted(map(lambda fr: fr[0], filter(lambda fr: fr[1], zip(families, check_results))))
    return available_families

def get_records(db_file):
    with open(db_file, 'r') as handle:
        records = list(SeqIO.parse(handle, 'fasta'))
    return records

def get_query_records(query):
    return get_records(join('../queries', query, query + '.db'))

def get_query_families(query):
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
    return get_bitscores(join('../queries', query, query + '.bitscore'))

def retain_bitscore_cols(cols, points, header):
    retain_idxs = []
    for col in cols:
        retain_idxs.append(header.index(col))

    new_header = []
    for i in retain_idxs:
        new_header.append(header[i])

    new_points = []
    for point in points:
        row = []
        for i in retain_idxs:
            row.append(point[i])
        new_points.append(row)
    return new_points, new_header

def run_command(command, verbose=False):
    import subprocess
    error = False

    if verbose == True:
        print command
        print ""

    job = subprocess.Popen(command, bufsize=0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    jobOutput = []
    if verbose == True:
        for line in job.stdout:
            print "   ", line,
            jobOutput.append(line)
    else:
        jobOutput = job.stdout.readlines()
    result = job.wait()
    if result != 0:
        error = True

    return (jobOutput, result, error)