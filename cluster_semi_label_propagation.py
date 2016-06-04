from sklearn.semi_supervised import LabelPropagation
from os.path import join
import time
from optparse import OptionParser

'''
Semi-supervised clustering using label propagation
This will definitely give lesser-than-actual number of clusters, becasue of the insufficient 'seed' families.
'''

def create_map(strings):
    all_strings = set(strings)
    all_int = [i for i in range(len(all_strings))]
    return dict(zip(all_strings, all_int)), dict(zip(all_int, all_strings))

def family_of(name):
    first = name.split('_')[0]
    if first[0] == 'Q':
        return first[1:]
    else:
        return first

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

centroid_names = []
centroid_points = []

test_names = []
test_points = []

with open(file, 'r') as handle:
    bitscore_header = handle.readline().strip().split('\t')
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))

        if name.split('_')[0][:2] == 'RF':
            # ignore the centroids (we will use it later)
            if name.find('_centroid') == -1:
                names.append(name)
                points.append(scores)
            else:
                centroid_names.append(name)
                centroid_points.append(scores)
        else:
            test_names.append(name)
            test_points.append(scores)

family_to_int, int_to_family = create_map(map(family_of, names))

print('having', len(points) + len(test_points) + len(centroid_points), 'points')

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
        # handle.write(int_to_family[label] + '\n')
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')

centroid_file = join('Rfam-seed', 'combined.' + tag + '.centroid.pcNorm' + str(len(bitscore_header)) + '.zNorm.bitscore')
with open(centroid_file, 'w') as handle:
    handle.write('\t'.join(bitscore_header) + '\n')
    for name, scores in zip(centroid_names, centroid_points):
        handle.write(name + '\t')
        for score in scores:
            handle.write(str(score) + '\t')
        handle.write('\n')

print('saving done!', len(clusters), 'clusters')