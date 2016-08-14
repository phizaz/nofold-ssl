from os.path import join
from Bio import SeqIO

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

class Mapper:

    def __init__(self, idxs, vectors, cols):
        self.vectors = vectors

        self.min_idx = min(idxs)
        self.max_idx = max(idxs)

        self.map_idx = dict(zip(idxs, [i for i in range(0, len(idxs))]))
        self.map_col = dict(zip(cols, [i for i in range(0, len(cols))]))

    def get(self, idx, col):
        idx = min(idx, self.max_idx)
        idx = max(idx, self.min_idx)
        i = self.map_idx[idx]
        c = self.map_col[col]
        return self.vectors[i][c]

class LengthNormalizer:

    def __init__(self):
        def read_file(file):
            idxs = []
            vectors = []
            with open(file, 'r') as handle:
                cols = handle.readline().strip().split()
                for line in handle:
                    tokens = line.strip().split()
                    length_id = int(tokens[0])
                    if any(token == 'NA' for token in tokens[1:]):
                        continue
                    digits = map(float, tokens[1:])
                    idxs.append(length_id)
                    vectors.append(digits)
            return idxs, vectors, cols

        means_file = join('../norm', 'varlen2.scale_means.txt')
        sds_file = join('../norm', 'varlen2.scale_sds.txt')

        self.mean_mapper = Mapper(*read_file(means_file))
        self.sd_mapper = Mapper(*read_file(sds_file))

    def length_normalize(self, col, length, x):
        return (x - self.mean_mapper.get(length, col)) / self.sd_mapper.get(length, col)

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

