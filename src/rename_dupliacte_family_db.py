from os.path import join, isdir
from os import listdir
from Bio import SeqIO

path = '../Rfam-seed/db'
families = [f for f in listdir(path) if isdir(join(path, f))]

def rename_family_db(family):
    fam_path = join(path, family)
    db_path = join(fam_path, family + '.db')
    with open(db_path, 'r') as handle:
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

    with open(db_path, 'w') as handle:
        SeqIO.write(results, handle, 'fasta')

for family in families:
    print('renaming', family)
    rename_family_db(family)
