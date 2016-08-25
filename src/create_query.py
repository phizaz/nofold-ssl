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
from itertools import product
import numpy as np
import sys


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


def save_records(file, records):
    seq_records = map(bioseq_of, records)
    with open(file, 'w') as handle:
        SeqIO.write(seq_records, handle, 'fasta')


def records_of(fam):
    with gzip.open(join(rfam_path, fam + '.fa.gz')) as handle:
        return list(SeqIO.parse(handle, 'fasta'))


query = 'fam40_typedistributed'

# a =transition_freq('RYKMSWBDHNVN')
# print(a.keys())
# sys.exit()

rfam_path = '/Volumes/Konpat/Rfam 12.1'
selected_fams = ['RF01848', 'RF02044', 'RF00727', 'RF02402', 'RF01607', 'RF01687', 'RF01685', 'RF02375', 'RF02514',
                 'RF01660', 'RF01225', 'RF01323', 'RF01689', 'RF00052', 'RF01786', 'RF02089', 'RF01482', 'RF01909',
                 'RF01929', 'RF01833', 'RF01501', 'RF01500', 'RF01505', 'RF01504', 'RF01506', 'RF01293', 'RF00381',
                 'RF00027', 'RF02045', 'RF00222', 'RF00104', 'RF00103', 'RF01930', 'RF01931', 'RF01932', 'RF01933',
                 'RF01934', 'RF01496', 'RF01499', 'RF01498']

total_seq_cnt = 1000
seq_per_fam = int(total_seq_cnt / len(selected_fams))

all_raw_records = []
all_sampled_records = []
all_embed_records = []
all_embed_sampled_records = []

# create name map database
name_map = dict()
for fam in selected_fams:
    raw_records = []
    for i, record in enumerate(records_of(fam)):
        name = 'Q' + fam + '_' + ('%05d' % i)
        name_map[name] = record.name

        raw_records.append((fam, name, str(record.seq)))
    all_raw_records += raw_records

    sampled_records = sample(raw_records, seq_per_fam)
    embed_records = embed(raw_records, (10, 50))
    embed_sampled_records = sample(embed_records, seq_per_fam)

    all_sampled_records += sampled_records
    all_embed_records += embed_records
    all_embed_sampled_records += embed_sampled_records

all_bg_records = generate_background(all_raw_records, 3 * len(all_sampled_records), 'bg')
all_embed_bg_records = generate_background(all_embed_records, 3 * len(all_embed_sampled_records), 'bg_embed')

print('saving..')
save_records(join('../queries', query, query + '.db'), all_sampled_records)
save_records(join('../queries', query + '_embed', query + '_embed.db'), all_embed_sampled_records)
save_records(join('../queries', query + '_bg', query + '_bg.db'), all_bg_records)
save_records(join('../queries', query + '_embed_bg', query + '_embed_bg' + '.db'), all_embed_bg_records)
print('done..')

with open(join('../queries', query + '.namemap'), 'w') as handle:
    for key, val in name_map.items():
        handle.write(key + ' ' + val + '\n')
