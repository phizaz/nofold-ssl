import utils
from itertools import chain
from os.path import join
from Bio import SeqIO

queries = ['fam40_typedistributed-rename', 'fam40_typedistributed_bg-rename']
name = 'fam40_typedistributed_plain_bg'

def combine(queries):
    for query in queries:
        if not utils.check_query(query):
            print('query {} is not ready'.format(query))
            return False

    # combine db
    records = list(chain.from_iterable(map(utils.get_query_records, queries)))
    names = []
    points = []
    header = None
    for query in queries:
        n, p, h = utils.get_query_bitscores(query)
        names += n
        points += p
        if header is None:
            header = h
        else:
            if header != h:
                print('variance in header')
                return False

    return records, (names, points, header)

def save_records(query, records):
    path = join('../queries', query)
    utils.make_path(path)
    file = join(path, '{}.db'.format(query))
    for record in records:
        record.description = ''
    with open(file, 'w') as handle:
        SeqIO.write(records, handle, 'fasta')

def save_bitscores(query, names, points, header):
    path = join('../queries', query)
    utils.make_path(path)
    file = join(path, '{}.bitscore'.format(query))
    with open(file, 'w') as handle:
        handle.write('{}\n'.format('\t'.join(header)))
        for name, point in zip(names, points):
            handle.write('{}\t{}\n'.format(name, '\t'.join(map(str, point))))

result = combine(queries)
if not result:
    print('something wrong')
else:
    # save to file
    records, (names, points, header) = result
    save_records(name, records)
    save_bitscores(name, names, points, header)
    print('done')

