from os.path import join, isdir
from os import listdir
from Bio import SeqIO

def rename_db(db_file):
    with open(db_file, 'r') as handle:
        records = SeqIO.parse(handle, 'fasta')
        have = dict()
        results = []
        for record in records:
            if record.name not in have:
                have[record.name] = 1
            else:
                # rename
                seq_no = have[record.name] + 1
                have[record.name] = seq_no
                record.name += ':' + str(seq_no)
                print('duplicate', record.name)

            record.id = record.name
            record.description = ''
            results.append(record)

    with open(db_file, 'w') as handle:
        SeqIO.write(results, handle, 'fasta')

rename_db(join('../queries', 'query', 'query.db'))
rename_db(join('../queries', 'query2', 'query2.db'))
rename_db(join('../queries', 'query3', 'query3.db'))