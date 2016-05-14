from lmethod import get_clusters_cnt
from sklearn.cluster import AgglomerativeClustering

file = 'Rfam-seed/combined.zNorm.pcNorm100.bitscore'

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

print('calculating number of clusters using l-method..')
cluster_cnt = get_clusters_cnt(points, linkage='ward')

print('clustering data into', cluster_cnt, 'clusters')
agg = AgglomerativeClustering(n_clusters=cluster_cnt, linkage='ward')
agg.fit(points)

labels = agg.labels_

print('saving results to file')
outfile = 'Rfam-seed/combined.lmethod.cluster'
clusters = [[] for i in range(cluster_cnt)]
for name, label in zip(names, labels):
    clusters[label].append(name)

with open(outfile, 'w') as handle:
    for label in range(cluster_cnt):
        for name in clusters[label]:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!')