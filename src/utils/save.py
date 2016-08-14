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

def save_bitscores(file, names, points, header):
    from os.path import join, dirname
    from .path import make_path
    path = dirname(file)
    make_path(path)
    with open(file, 'w') as handle:
        handle.write('{}\n'.format('\t'.join(header)))
        for name, point in zip(names, points):
            handle.write('{}\t{}\n'.format(name, '\t'.join(map(str, point))))

def save_query_bitscores(query, names, points, header):
    from os.path import join
    from .path import queries_path

    file = join(queries_path(), query, query + '.bitscore')
    return save_bitscores(file, names, points, header)


def save_name_clusters(file, clusters):
    with open(file, 'w') as handle:
        if isinstance(clusters, dict):
            clusters = clusters.items()
        elif isinstance(clusters, list):
            clusters = enumerate(clusters)
        else:
            raise Exception('alien clusters')
        for label, names in clusters:
            handle.write(
                ' '.join(names) + '\n'
            )
