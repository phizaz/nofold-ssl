from src import utils

if __name__ == '__main__':
    query = 'gencode.v25.lncRNA-rename'
    records = utils.get.get_query_records(query)

    new_query = 'gencode.v25.lncRNA-short'
    new_records = list(filter(lambda x: len(x.seq) < 1000, records))

    from os.path import join
    outfile = join(utils.path.queries_path(), new_query, '{}.db'.format(new_query))
    utils.save.save_records(new_records, outfile)
