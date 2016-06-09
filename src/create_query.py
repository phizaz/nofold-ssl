from __future__ import division
from os.path import join, exists
import utils
import gzip
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import SingleLetterAlphabet, RNAAlphabet, DNAAlphabet
from Bio.SeqRecord import SeqRecord
from collections import Counter
from random import randint, sample
from itertools import product
import numpy as np
import sys

expand_map = {
    'A': ('A'),
    'C': ('C'),
    'G': ('G'),
    'T': ('T'),
    'U': ('U'),
    'R': ('A', 'G'),
    'Y': ('C', 'T', 'U'),
    'K': ('G', 'T', 'U'),
    'M': ('A', 'C'),
    'S': ('C', 'G'),
    'W': ('A', 'T', 'U'),
    'B': ('C', 'G', 'T', 'U'),
    'D': ('A', 'G', 'T', 'U'),
    'H': ('A', 'C', 'T', 'U'),
    'V': ('A', 'C', 'G'),
    'N': ('A', 'C', 'G', 'T', 'U')
}

def expand(a, possibles='ACGT'):
    return set(expand_map[a]) & set(possibles)

def expand_tuple(aa, possibles='ACGT'):
    a, b = aa
    aa, bb = expand(a, possibles), expand(b, possibles)
    return [''.join(r) for r in product(aa, bb)]

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

def weighted_random(cnt, possibles, weights=None):
    return np.random.choice(possibles, cnt, p=weights)

def sliding_window(itr, window_size):
    results = [''] * window_size
    for i, val in enumerate(itr):
        pos = i % window_size
        results[pos] = val
        if i >= window_size - 1:
            yield tuple(results[i] for i in range(pos + 1, window_size) + range(0, pos + 1))

def zeros():
    while True:
        yield 0

def dinuc_freq(sequence, possibles='ACGT'):
    assert len(possibles) == 4
    possible_dinucs = map(lambda x: ''.join(x), product(possibles, possibles))
    counter = Counter(dict(zip(possible_dinucs, zeros())))
    for each in sliding_window(sequence, 2):
        expanded = Counter(expand_tuple(each, possibles))
        counter.update(expanded)
    return counter

def transition_freq(sequence, possibles='ACGT'):
    assert len(possibles) == 4
    possible_dinucs = map(lambda x: ''.join(x), product(possibles, possibles))
    counter = dict()
    for a in possible_dinucs:
        counter[a] = Counter(dict(zip(possible_dinucs, zeros())))

    dinuc = map(lambda x: ''.join(x), sliding_window(sequence, 2))

    for a, b in sliding_window(dinuc, 2):
        aa = expand_tuple(a, possibles)
        bb = expand_tuple(b, possibles)
        for aaa, bbb in product(aa, bb):
            counter[aaa][bbb] += 1

    return counter

def normalize(l):
    total = sum(l)
    result = []
    for each in l: result.append(each / total)
    return result

def generate_background_each(size, begin_prob, trans_prob):
    begin = ''.join(weighted_random(1, begin_prob.keys(), begin_prob.values()))
    result = list(begin)
    current = begin
    while len(result) < size:
        prob = trans_prob[current]
        next = weighted_random(1, prob.keys(), prob.values())[0]
        a, b = next
        result.append(b)
        current = next

    return ''.join(result)

def get_length_distribution(strings):
    counter = Counter(map(len, strings))
    return dict(zip(counter.keys(), normalize(counter.values())))

def generate_background(records, generate_size):
    sequences = map(seq_of, records)
    length_distribution = get_length_distribution(sequences)
    long_sequence = ''.join(sequences)
    possibles = set(long_sequence)

    if 'U' in possibles:
        possibles = 'ACGU'
    else:
        possibles = 'ACGT'
    print('possibles:', possibles)

    print('creating transition freq...')
    trans_freq = transition_freq(long_sequence, possibles)

    begin_weigths = normalize(map(lambda x: sum(x.values()), trans_freq.values()))
    begin_prob = dict(zip(trans_freq.keys(), begin_weigths))

    trans_prob = dict()
    for key, prob in trans_freq.items():
        trans_prob[key] = dict(zip(prob.keys(), normalize(prob.values())))

    print('generating background...')
    results = []
    for i in range(generate_size):
        name = 'bg_' + str(i + 1)
        length = weighted_random(1, length_distribution.keys(), length_distribution.values())[0]
        print('seq:', i, 'len:', length)
        seq = generate_background_each(length, begin_prob, trans_prob)
        results.append(('bg', name, seq))

    return results

def embed_sequence(sequence, embed_size):
    distribution = get_char_distribution(sequence)
    embed_front = ''.join(weighted_random(embed_size, distribution.keys(), distribution.values()))
    embed_rear = ''.join(weighted_random(embed_size, distribution.keys(), distribution.values()))
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

query = 'fam40_typedistributed'

# a =transition_freq('RYKMSWBDHNVN')
#print(a.keys())
#sys.exit()

rfam_path = '/Volumes/Konpat/Rfam 12.1'
selected_fams = ['RF01848', 'RF02044', 'RF00727', 'RF02402', 'RF01607', 'RF01687', 'RF01685', 'RF02375', 'RF02514', 'RF01660', 'RF01225', 'RF01323', 'RF01689', 'RF00052', 'RF01786', 'RF02089', 'RF01482', 'RF01909', 'RF01929', 'RF01833', 'RF01501', 'RF01500', 'RF01505', 'RF01504', 'RF01506', 'RF01293', 'RF00381', 'RF00027', 'RF02045', 'RF00222', 'RF00104', 'RF00103', 'RF01930', 'RF01931', 'RF01932', 'RF01933', 'RF01934', 'RF01496', 'RF01499', 'RF01498']

total_seq_cnt = 1000
seq_per_fam = int(total_seq_cnt / len(selected_fams))

all_embed_records = []
all_raw_records = []
all_sampled_records = []
for fam in selected_fams:
    print('fam:', fam)
    names_taken = Counter()
    with gzip.open(join(rfam_path, fam + '.fa.gz')) as handle:
        raw_records = map(lambda x: (fam, x.name, str(x.seq)),SeqIO.parse(handle, 'fasta'))
        print('size:', len(raw_records))

        all_raw_records += raw_records

        sampled_records = sample(raw_records, seq_per_fam)
        print(sampled_records)

        all_sampled_records += sampled_records

        records = []
        for _, name, seq in sampled_records:
            decorated_name = decorate_name(fam, name)
            names_taken[decorated_name] += 1

            if names_taken[decorated_name] > 1:
                decorated_name += ':' + str(names_taken[decorated_name])

            records.append((fam, decorated_name, seq))

        embed_records = embed(records, (10, 50))
        all_embed_records += embed_records

all_bg_records = generate_background(all_raw_records, 3 * len(all_sampled_records))
print(len(all_bg_records))

print('saving..')
save_records(join('../quries', query, query + '.db'), all_sampled_records)
save_records(join('../quries', query + '_embed', query + '_embed.db'), all_embed_records)
save_records(join('../quries', query + '_bg', query + '_bg.db'), all_sampled_records + all_bg_records)
save_records(join('../quries', query + '_embed_bg', query + '_embed_bg' + '.db'), all_embed_records + all_bg_records)
print('done..')