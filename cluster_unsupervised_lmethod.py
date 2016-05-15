from lmethod import agglomerative_l_method
from os.path import join

tag = 'query.cripple25'
file = join('Rfam-seed', 'combined.' + tag + '.zNorm.pcNorm100.bitscore')

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

print('cluster using l-method..')
agg = agglomerative_l_method(points, method='ward')
labels = agg.labels_
cluster_cnt = max(labels) + 1

print('saving results to file')
outfile = join('Rfam-seed', 'combined.' + tag + '.lmethod-ward.cluster')
clusters = [[] for i in range(cluster_cnt)]
for name, label in zip(names, labels):
    clusters[label].append(name)

with open(outfile, 'w') as handle:
    for label in range(cluster_cnt):
        for name in clusters[label]:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!')