def save_query_records(query, records):
    from os.path import join
    from .path import make_path, queries_path
    from Bio import SeqIO

    path = join(queries_path(), query)
    make_path(path)
    file = join(path, '{}.db'.format(query))
    for record in records:
        record.description = ''
    with open(file, 'w') as handle:
        SeqIO.write(records, handle, 'fasta')


def save_bitscores(query, names, points, header):
    from os.path import join
    from .path import make_path, queries_path

    path = join(queries_path(), query)
    make_path(path)
    file = join(path, '{}.bitscore'.format(query))
    with open(file, 'w') as handle:
        handle.write('{}\n'.format('\t'.join(header)))
        for name, point in zip(names, points):
            handle.write('{}\t{}\n'.format(name, '\t'.join(map(str, point))))
