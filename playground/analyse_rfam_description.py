from __future__ import division
import csv
from collections import Counter
import numpy as np
from operator import itemgetter

def create_map(strings):
    all_strings = set(strings)
    all_int = [i for i in range(len(all_strings))]
    str_to_int = dict(zip(all_strings, all_int))
    int_to_str = dict(zip(all_int, all_strings))

    def map_to_int(string):
        return str_to_int[string]

    def map_to_str(int):
        return int_to_str[int]

    return map_to_int, map_to_str

def bit_transform(types):
    have = np.zeros(len(possible_types))
    for t in types:
        s = to_int(t)
        have[s] = 1
    return have

def score(bits, distribution):
    s = 0
    for a, expect in zip(bits, distribution):
        s += min(a, expect)
    return s

def discretize(bits):
    return np.array(map(float, map(int, bits)))


file = 'rfam_description.csv'

select_family_cnt = 40
select_sequence_cnt = 1000
select_per_family = select_sequence_cnt / select_family_cnt

families = []
type_freq = Counter()
with open(file, 'r') as handle:
    reader = csv.reader(handle, delimiter=',')
    for name, fam, type, seed, full, description in reader:
        types = filter(lambda x: x, map(lambda x: x.strip(), type.strip().split(';')))
        for t in types:
            type_freq[t] += 1

        families.append((name, fam, types, int(seed), int(full), description))

possible_types = type_freq.keys()
print('possible types:', possible_types)
to_int, to_type = create_map(possible_types)

distrubition = np.zeros(len(possible_types))
weights = np.ones(len(possible_types))
for type, freq in sorted(type_freq.items(), key=lambda x: -x[1]):
    weighted_freq = freq / len(families)
    distrubition[to_int(type)] = weighted_freq
    print type, ':', freq

print('type cnt:', len(type_freq))
print('distribution:', distrubition)

bits = map(bit_transform, map(itemgetter(2), families))
fam_bits = sorted(zip(families, bits), key=lambda x: -sum(x[1]))
max_bit_cnt = int(sum(fam_bits[0][1]))
print('max_bit_cnt:', max_bit_cnt)

have = np.zeros(len(possible_types))

# more lnc RNA
# weights[to_int('lncRNA')] = 3

expected_distribution = distrubition * weights * 40 # arbitrary number

print('expected_distribution:')
print(discretize(expected_distribution))

last_score = score(have, expected_distribution)
picked = set()
for threshold in range(max_bit_cnt, 0, -1):
    # don't over pick
    if len(picked) >= select_family_cnt:
        break

    for (name, fam, types, seed, full, description), bits in fam_bits:
        # family doesn't have enough sequences
        if full < select_per_family:
            continue

        # don't pick many times
        if fam in picked:
            continue

        tmp = have + bits
        new_score = score(tmp, expected_distribution)
        if new_score - last_score >= threshold:
            picked.add(fam)
            have = tmp
            last_score = new_score

        if len(picked) >= select_family_cnt:
            break

print('picked:', len(picked))
print(have)
l = list(enumerate(have))
l.sort(key=lambda x: -x[1])
for i, each in l:
    if each > 0:
        print to_type(i), ':', int(each)
print(picked)


