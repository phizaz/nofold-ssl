from sklearn import datasets
from random import sample
from sklearn.semi_supervised import LabelPropagation
import numpy as np
import matplotlib.pyplot as plt

'''
a demonstration of LabelPropagation on a dataset that has unlabeled group in the center, kinda being tugged towards both ends
If both distances are the same, the center group is equalled separated
If not (even a little), the center is much dominated by the closer one.
'''

def gaussian(mean, size, count):
    cov = [[size, 0], [0, size]]
    return np.random.multivariate_normal(mean, cov, count)

def gaussian_with_labels(mean, size, count, label = None, label_count = 0):
    points = gaussian(mean, size, count)
    labels = [-1 for i in range(len(points))]
    if label_count > 0:
        for idx in sample(range(0, len(points)), label_count):
            labels[idx] = label
    return points, labels

def concatenate(t):
    points = np.concatenate([p[0] for p in t])
    labels = np.concatenate([p[1] for p in t])
    return points, labels

def points_by_label(points, labels, label):
    out_points = []
    out_labels = []
    for p, l in zip(points, labels):
        if l == label:
            out_points.append(p)
            out_labels.append(l)
    return np.array(out_points), np.array(out_labels)

points, labels = concatenate((
    gaussian_with_labels((0, 0), 1, 100, 0, 5),
    gaussian_with_labels((5, 5), 1, 100),
    gaussian_with_labels((10, 10), 1, 100, 1, 5)
))

ssl = LabelPropagation()
ssl.fit(points, labels)
labels = ssl.predict(points)

fig, ax = plt.subplots()

#b_points, b_labels = points_by_label(points, labels, -1)
#X, Y = b_points.T
#ax.scatter(X, Y, c='grey')

a_points, a_labels = points_by_label(points, labels, 0)
X, Y = a_points.T
ax.scatter(X, Y, c='red')

c_points, c_labels = points_by_label(points, labels, 1)
X, Y = c_points.T
ax.scatter(X, Y, c='blue')

plt.show()

