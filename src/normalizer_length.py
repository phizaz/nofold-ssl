from os.path import join
import bisect as bs
from Bio import SeqIO
import utils

class Lengther:
    def __init__(self, query, names):
        def open_file(file):
            with open(file, 'r') as handle:
                records = SeqIO.parse(handle, 'fasta')
                length_name = {}
                for record in records:
                    length_name[record.name] = len(record.seq)
            return length_name

        self.length_name = {}

        # get length from the query itself
        db_file = join('../queries', query, query + '.db')
        files = [db_file]

        required_families = set()
        for name in names:
            fam = name.split('_')[0]
            if fam[:2] == 'RF':
                required_families.add(fam)

        print('required families:', required_families)
        print('count:', len(required_families))

        for fam in required_families:
            files.append(join('../Rfam-seed/db', fam, fam + '.db'))

        for file in files:
            self.length_name.update(open_file(file))

    def length_of(self, name):
        return self.length_name[name]

class LengthNormalizer:

    def __init__(self):
        def floater(cell):
            return 'NA' if cell == 'NA' else float(cell)

        def possible_length(col):
            return map(lambda x: x[col] != 'NA', self.db_means)

        def transform(l):
            # l = [0, 1]* -> l = [1,3,5,9] according to the 1 positions
            results = []
            for i, each in enumerate(l):
                if each: results.append(i)
            return results

        def read_file(file):
            results = []
            with open(file, 'r') as handle:
                cols = handle.readline().strip().split()
                for line in handle:
                    tokens = line.strip().split()
                    # length_id = tokens[0]
                    digits = map(floater, tokens[1:])
                    results.append(dict(zip(cols, digits)))
            return results

        means_file = join('../norm', 'varlen2.scale_means.txt')
        sds_file = join('../norm', 'varlen2.scale_sds.txt')

        self.db_means = read_file(means_file)
        self.db_sds = read_file(sds_file)

        cols = self.db_means[0].keys()
        increasing_list = map(possible_length, cols)
        self.possible_length_actual = dict(zip(cols, increasing_list))
        self.possible_length_list = dict(zip(cols, map(transform, increasing_list)))

    def closest_length(self, length, col):
        if length < len(self.possible_length_actual[col]) and self.possible_length_actual[col][length]:
            return length

        # print('col:', col, 'length:', length)
        pos = bs.bisect_left(self.possible_length_list[col], length)
        before = self.possible_length_list[col][pos]
        # it is more than we have
        if pos == len(self.possible_length_list[col]) - 1:
            return before

        # return the closest one
        after = self.possible_length_list[col][pos + 1]
        if length - before < after - length:
            return before
        else:
            return after

    def length_normalize(self, col, length, x):
        c_length = self.closest_length(length, col)
        return (x - self.db_means[c_length][col]) / self.db_sds[c_length][col]

    def length_normalize_full(self, names, points, header, query):
        assert len(points[0]) == len(header)

        lengther = Lengther(query, names)

        normalized_points = []
        for name, scores in zip(names, points):
            point = []
            for col, digit in zip(header, scores):
                point.append(self.length_normalize(col, lengther.length_of(name), digit))
            normalized_points.append(point)

        return normalized_points

