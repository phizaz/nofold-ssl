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
    from itertools import product
    a, b = aa
    aa, bb = expand(a, possibles), expand(b, possibles)
    return [''.join(r) for r in product(aa, bb)]


def dinuc_freq(sequence, possibles='ACGT'):
    assert len(possibles) == 4
    from collections import Counter
    from src.utils.short import sliding_window, zeros
    from itertools import product

    possible_dinucs = map(lambda x: ''.join(x), product(possibles, possibles))
    counter = Counter(dict(zip(possible_dinucs, zeros())))
    for each in sliding_window(sequence, 2):
        expanded = Counter(expand_tuple(each, possibles))
        counter.update(expanded)
    return counter


def transition_freq(sequence, possibles='ACGT'):
    assert len(possibles) == 4
    from collections import Counter
    from itertools import product
    from src.utils.short import sliding_window, zeros

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


def generate_background_each(size, begin_prob, trans_prob):
    from src.utils.short import weighted_random

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
    from collections import Counter
    from src.utils.short import unit_normalize

    counter = Counter(map(len, strings))
    return dict(zip(counter.keys(), unit_normalize(counter.values())))


def generate_background(records, generate_size, namespace='bg'):
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
        name = namespace + str(i + 1)
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
