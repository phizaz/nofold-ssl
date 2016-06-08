from __future__ import division
from os.path import join, exists
import utils
import gzip
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import SingleLetterAlphabet
from Bio.SeqRecord import SeqRecord
from collections import Counter
from random import randint, sample
import numpy as np

# record = (fam, name, sequence)

def fam_of(record):
    return record[0]

def name_of(record):
    return record[1]

def seq_of(record):
    return record[2]

def decorate_name(fam, name):
    return fam + '_' + name.split('/')[0]

def get_char_distribution(string):
    counter = Counter()
    for char in string:
        counter[char] += 1
    for key in counter.keys():
        counter[key] /= len(string)
    return counter

def bioseq_of((fam, name, sequence)):
    return SeqRecord(Seq(sequence, SingleLetterAlphabet),
                     id=name, name=name, description='')

def weighted_random(cnt, possibles, weights):
    return ''.join(np.random.choice(possibles, cnt, p=weights))

def generate_background(records, generate_size):
    pass

def embed_sequence(sequence, embed_size):
    distribution = get_char_distribution(sequence)
    embed_front = weighted_random(embed_size, distribution.keys(), distribution.values())
    embed_rear = weighted_random(embed_size, distribution.keys(), distribution.values())
    return embed_front + sequence + embed_rear

def embed(records, (embed_min_length, embed_max_length)):
    results = []
    for fam, name, sequence in records:
        embed_size = randint(embed_min_length, embed_max_length)
        results.append((fam, name + '_emb', embed_sequence(sequence, embed_size)))
    return results

def save_records(file, records):
    seq_records = map(bioseq_of, records)
    with open(file, 'w') as handle:
        SeqIO.write(seq_records, handle, 'fasta')

query = 'fam40_typedistributed_embedded'

rfam_path = '/Volumes/Konpat/Rfam 12.1'
selected_fams = ['RF01848', 'RF02044', 'RF00727', 'RF02402', 'RF01607', 'RF01687', 'RF01685', 'RF02375', 'RF02514', 'RF01660', 'RF01225', 'RF01323', 'RF01689', 'RF00052', 'RF01786', 'RF02089', 'RF01482', 'RF01909', 'RF01929', 'RF01833', 'RF01501', 'RF01500', 'RF01505', 'RF01504', 'RF01506', 'RF01293', 'RF00381', 'RF00027', 'RF02045', 'RF00222', 'RF00104', 'RF00103', 'RF01930', 'RF01931', 'RF01932', 'RF01933', 'RF01934', 'RF01496', 'RF01499', 'RF01498']

total_seq_cnt = 1000
seq_per_fam = int(total_seq_cnt / len(selected_fams))

all_embed_records = []
for fam in selected_fams:
    print('fam:', fam)
    names_taken = Counter()
    with gzip.open(join(rfam_path, fam + '.fa.gz')) as handle:
        raw_records = list(SeqIO.parse(handle, 'fasta'))
        print('size:', len(raw_records))

        sampled_records = sample(raw_records, seq_per_fam)
        print(sampled_records)

        records = []
        for record in sampled_records:
            decorated_name = decorate_name(fam, record.name)
            names_taken[decorated_name] += 1

            if names_taken[decorated_name] > 1:
                decorated_name += ':' + str(names_taken[decorated_name])

            records.append((fam, decorated_name, str(record.seq)))

        embed_records = embed(records, (10, 50))
        all_embed_records += embed_records

print('saving..')
save_records(join('../quries', query, query + '.db'), all_embed_records)
print('done..')