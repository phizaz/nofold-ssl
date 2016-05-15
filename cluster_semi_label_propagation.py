from sklearn.semi_supervised import LabelPropagation
from os.path import join
import time
from optparse import OptionParser

def create_map(strings):
    all_strings = set(strings)
    all_int = [i for i in range(len(all_strings))]
    return dict(zip(all_strings, all_int)), dict(zip(all_int, all_strings))

def family_of(name):
    family, rest = name.split('_')
    return family

parser = OptionParser(usage='cluster using semi-supervised label propagation algorithm')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
parser.add_option("--kernel", action="store", default='rbf', dest="KERNEL", help="kernel")
parser.add_option("--gamma", action="store", type='float', default=1, dest="GAMMA", help="rbf kernel's gamma")
parser.add_option("--nn", action="store", type='int', default=19, dest="NN", help="knn's nearest neighbor parameter")
parser.add_option("--components", action="store", type='int', default=100, dest="COMPONENTS", help="PCA's number of components")
(opts, args) = parser.parse_args()

tag = opts.TAG
file = join('Rfam-seed', 'combined.' + tag + '.pcNorm' + str(opts.COMPONENTS) + '.zNorm.bitscore')

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

family_to_int, int_to_family = create_map(map(family_of, names))

print('having', len(points) + len(test_points), 'points')

print('training the label propagation')
start_time = time.time()
if opts.KERNEL == 'knn':
    print('n_neighbors:', opts.NN)
    ssl = LabelPropagation(kernel='knn', n_neighbors=opts.NN)
elif opts.KERNEL == 'rbf':
    print('gamma:', opts.GAMMA)
    ssl = LabelPropagation(kernel='rbf', gamma=opts.GAMMA)
X = points + test_points
Y = list(map(lambda n: family_to_int[n], map(family_of, names))) + [-1 for i in range(len(test_names))]
ssl.fit(X, Y)
labels = ssl.transduction_[len(points):]
end_time = time.time()
print('training took:', end_time - start_time, 'seconds')

clusters = {}
for name, label in zip(test_names, labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(name)

print('saving results to file')
outfile = join('Rfam-seed', 'combined.' + tag + '.labelPropagation.cluster')
with open(outfile, 'w') as handle:
    for label, members in clusters.items():
        # handle.write(int_to_family[label] + ' ')
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!', len(clusters), 'clusters')