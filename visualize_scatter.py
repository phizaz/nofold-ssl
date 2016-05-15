import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

'''
visualization using 2d scatter plot with PCA is not gonna give us anything.
'''

file = 'Rfam-seed/combined.zNorm.pcNorm100.bitscore'

all_names = []
all_scores = []
with open(file, 'r') as handle:
    handle.readline()
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        name, scores = tokens[0], list(map(float, tokens[1:]))
        all_names.append(name)
        all_scores.append(scores)

pca = PCA(n_components=2)
all_scores = pca.fit_transform(all_scores)

fig, ax = plt.subplots()

X, Y = all_scores.T

ax.scatter(X, Y)
ax.set_xlim([-3, 3])
ax.set_ylim([-3, 3])

plt.show()