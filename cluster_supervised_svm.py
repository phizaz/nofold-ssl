from sklearn.svm import SVC

'''
svm takes to much time on multi-class classification, not to be used in this experiment
'''

file = 'Rfam-seed/combined.zNorm.pcNorm100.zNorm.bitscore'

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

print('having', len(points) + len(test_points), 'points')

print('training the SVM..')
svm = SVC(kernel='linear')
svm.fit(points, names)

print('classifying data using SVM')
labels = svm.predict(test_points)
print('labels:', labels)

print('saving results to file')
outfile = 'Rfam-seed/combined.svm.cluster'
clusters = {}
for name, label in zip(test_names, labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(name)

with open(outfile, 'w') as handle:
    for label, members in clusters.items():
        for name in members:
            handle.write(name + ' ')
        handle.write('\n')

print('saving done!')