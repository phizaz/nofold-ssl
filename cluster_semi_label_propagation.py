from sklearn.semi_supervised import LabelPropagation

def create_map(strings):
    all_strings = set(strings)
    all_int = [i for i in range(len(all_strings))]
    return dict(zip(all_strings, all_int)), dict(zip(all_int, all_strings))

file = 'Rfam-seed/combined.zNorm.pcNorm100.bitscore'

names = []
points = []

test_names = []
test_points = []

with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))

        if name.split('_')[0][:2] == 'RF':
            names.append(name)
            points.append(scores)
        else:
            test_names.append(name)
            test_points.append(scores)

family_to_int, int_to_family = create_map(names)

print('having', len(points) + len(test_points), 'points')

print('training the label propagation')
ssl = LabelPropagation(kernel='knn', n_neighbors=17)
X = points + test_points
Y = list(map(lambda n: family_to_int[n], names)) + [-1 for i in range(len(test_names))]
ssl.fit(X, Y)
labels = ssl.predict(test_points)

clusters = {}
for name, label in zip(test_names, labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(name)

print('saving results to file')
outfile = 'Rfam-seed/combined.labelPropagation.cluster'
with open(outfile, 'w') as handle:
    for label, members in clusters.items():
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!')