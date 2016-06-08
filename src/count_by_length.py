import utils
from os.path import join
from multiprocessing.pool import Pool
from Bio import SeqIO

families = utils.get_calculated_families()

def count(family):
    bitscore_file = join('../Rfam-seed', 'db', family, family + '.bitscore')
    db_file = join('../Rfam-seed', 'db', family, family + '.db')

    with open(db_file, 'r') as handle:
        records = list(SeqIO.parse(handle, 'fasta'))
        names = map(lambda x: x.name, records)
        lengths = map(lambda x: len(x.seq), records)
        length_by_name = dict(zip(names, lengths))

    with open(bitscore_file, 'r') as handle:
        cols = handle.readline().strip().split()
        cnt = {}
        for line in handle:
            tokens = line.strip().split()
            name, scores = tokens[0], map(float, tokens[1:])
            length = length_by_name[name]
            if length not in cnt:
                cnt[length] = 0
            cnt[length] += 1
    return cnt

pool = Pool()
results = pool.map(count, families)
pool.close()

cols = results[0].keys()
cnt = {}
for r in results:
    for length, num in r.items():
        if length not in cnt:
            cnt[length] = 0
        cnt[length] += num

print(cnt)