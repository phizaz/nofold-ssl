import utils
from itertools import chain
from os.path import join
from Bio import SeqIO
from argparse import ArgumentParser

parser = ArgumentParser(description='rename rna bitscore')
parser.add_argument('--query', action='store', required=True)
parser.add_argument('--output', action='store', required=True)
args = parser.parse_args()

queries = args.query.strip().split(',')
name = args.output

def combine(queries):
    for query in queries:
        if not utils.check.check_query(query):
            print('query {} is not ready'.format(query))
            return False

    # combine db
    records = list(chain.from_iterable(map(utils.get.get_query_records, queries)))
    names = []
    points = []
    header = None
    for query in queries:
        n, p, h = utils.get.get_query_bitscores(query)
        names += n
        points += p
        if header is None:
            header = h
        else:
            if header != h:
                print('variance in header')
                return False

    return records, (names, points, header)

result = combine(queries)
if not result:
    print('something wrong')
else:
    # save to file
    records, (names, points, header) = result
    utils.save.save_query_records(name, records)
    utils.save.save_query_bitscores(name, names, points, header)
    print('done')

