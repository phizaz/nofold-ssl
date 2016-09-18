from __future__ import print_function


def create_name(prefix, running_no):
    name = '{}_{:06}'.format(prefix, running_no)
    assert len(name) <= 25, '`{name}` max name length is 25 for reliable cmscore calculation'.format(name=name)
    return name


def short_name_formatted(name, running_no):
    # names originally should be prefixed with 'RF'
    # in the pattern RFXXXXX_REALLYLONGNAME
    # and will be prefixed with 'QRF'
    fam = name.split('_')[0]
    new_name = create_name(fam, running_no)
    return new_name


def short_name_unformatted(name, running_no, query):
    # names have no conventions
    # just shorten these names
    return create_name(query, running_no)


def shorten_names(names, query, formatted):
    from collections import OrderedDict
    new_to_old = OrderedDict()
    from itertools import count
    running_no = count(1)

    if formatted:
        new_names = [
            short_name_formatted(name, running_no.next())
            for name in names
            ]
    else:
        new_names = [
            short_name_unformatted(name, running_no.next(), query)
            for name in names
            ]

    for old_name, new_name in zip(names, new_names):
        new_to_old[new_name] = old_name

    return new_names, new_to_old


def save_new_to_old(new_to_old, query):
    from src import utils
    from os.path import join
    query_path = join(utils.path.queries_path(), query)
    query_db_namemap_path = join(query_path, '{}.namemap'.format(query))
    with open(query_db_namemap_path, 'w') as handle:
        for new_name, old_name in new_to_old.items():
            handle.write('{} {}\n'.format(new_name, old_name))


def read_new_to_old(query):
    from os.path import join
    from src import utils
    query_db_namemap_path = join(utils.path.queries_path(), query, '{}.namemap'.format(query))
    from collections import OrderedDict
    new_to_old = OrderedDict()
    with open(query_db_namemap_path) as handle:
        for line in handle:
            line = line.strip()
            new, old = line.split(' ')
            new_to_old[new] = old
    return new_to_old


def rename(records, query, formatted):
    names = [
        rec.name
        for rec in records
        ]

    new_names, new_to_old = shorten_names(names, query, formatted)
    from src import utils
    new_records = [
        utils.get.new_record(new_name, rec.seq)
        for new_name, rec in zip(new_names, records)
        ]
    return new_records, new_to_old


def new_query_name(query):
    return '{}-rename'.format(query)


def run_rename(query, formatted):
    from src import utils
    records = utils.get.get_query_records(query)
    new_records, new_to_old = rename(records, query, formatted)

    from src import utils
    from os.path import join, exists
    new_query = new_query_name(query)
    outpath = join(utils.path.queries_path(), new_query)

    from os import makedirs
    if not exists(outpath):
        makedirs(outpath)

    outfile = join(outpath, '{}.db'.format(new_query))
    # save
    utils.save.save_records(new_records, outfile)
    save_new_to_old(new_to_old, new_query)
    return new_records, new_to_old, new_query


def run_cmscore(query, cpu):
    from src.utils.helpers import cmscore
    from src import utils
    records = utils.get.get_query_records(query)
    cmscores = cmscore.get_cmscores(records, cpu=cpu)
    from os.path import join
    outfile = join(utils.path.queries_path(), query, '{}.bitscore'.format(query))
    cmscore.save_cmscores(cmscores, outfile)
    return cmscores


def main(query, cpu, should_rename, formatted):
    if should_rename:
        _, _, query = run_rename(query, formatted)

    cmscores = run_cmscore(query, cpu)
    return cmscores


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('query')
    parser.add_argument('--cpu', type=int)
    parser.add_argument('--rename', default=False, action='store_true')
    parser.add_argument('--formatted', default=False, action='store_true')
    args = parser.parse_args()

    main(args.query, args.cpu, args.rename, args.formatted)
