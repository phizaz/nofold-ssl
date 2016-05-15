from lmethod import agglomerative_l_method
from os.path import join
from optparse import OptionParser

parser = OptionParser(usage='cluster using semi-supervised label propagation algorithm')
parser.add_option("--tag", action="store", default='', dest="TAG", help="tag")
parser.add_option("--linkage", action="store", default='ward', dest="LINKAGE", help="linkage for hierarchical clustering")
parser.add_option("--components", action="store", type='int', default=100, dest="COMPONENTS", help="PCA's number of components")
(opts, args) = parser.parse_args()

tag = opts.TAG
file = join('Rfam-seed', 'combined.' + tag + '.pcNorm' + str(opts.COMPONENTS) + '.zNorm.bitscore')

names = []
points = []

with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))

        # take only the unlabeled ones, because l-method is an unsupervised approach
        if name.split('_')[0][:3] == 'QRF':
            names.append(name)
            points.append(scores)

print('having', len(points), 'points')

print('cluster using l-method linkage:', opts.LINKAGE)
agg = agglomerative_l_method(points, method=opts.LINKAGE)
labels = agg.labels_
cluster_cnt = max(labels) + 1

print('saving results to file')
outfile = join('Rfam-seed', 'combined.' + tag + '.lmethod.' + opts.LINKAGE + '.cluster')
clusters = [[] for i in range(cluster_cnt)]
for name, label in zip(names, labels):
    clusters[label].append(name)

with open(outfile, 'w') as handle:
    for label in range(cluster_cnt):
        for name in clusters[label]:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!')