from __future__ import division
from fastcluster import linkage
from collections import deque
from sklearn.metrics import mean_squared_error
import numpy
from sklearn.neighbors import BallTree
from itertools import islice

def f_creator(coef, intercept):
    def f(x):
        return intercept + coef * x

    return f

def best_fit_line(x, y):
    coef, intercept = numpy.polyfit(x, y, 1)
    return coef, intercept

def plot(X, fn):
    return [fn(x) for x in X]

def _l_method(num_groups, merge_dist):
    element_cnt = len(num_groups)

    # short circuit, since the l-method doesn't work with the number of elements below 4
    if element_cnt < 4:
        return 1

    # now we have some level of confidence that O(n) is not attainable
    # this l_method is gonna be slow... n * 2 * O(MSE)

    x_left = num_groups[:2]
    y_left = merge_dist[:2]

    # we use 'deque' data structure here to attain the efficient 'popleft'
    x_right = deque(num_groups[2:])
    y_right = deque(merge_dist[2:])

    min_score = float('inf')
    min_c = None

    for left_cnt in range(2, element_cnt - 2 + 1):
        # get best fit lines
        coef_left, intercept_left = best_fit_line(x_left, y_left)
        coef_right, intercept_right = best_fit_line(x_right, y_right)

        fn_left = f_creator(coef_left, intercept_left)
        fn_right = f_creator(coef_right, intercept_right)

        y_pred_left = plot(x_left, fn_left)
        y_pred_right = plot(x_right, fn_right)

        # calculate the error on each line
        mseA = mean_squared_error(y_left, y_pred_left)
        mseB = mean_squared_error(y_right, y_pred_right)

        # calculate the error on both line cumulatively
        A = left_cnt / element_cnt * mseA
        B = (element_cnt - left_cnt) / element_cnt * mseB
        score = A + B

        x_left.append(num_groups[left_cnt])
        y_left.append(merge_dist[left_cnt])

        x_right.popleft()
        y_right.popleft()

        if score < min_score:
            # find the best pair of best fit lines (that has the lowest mse)

            # left_cnt is not the number of clusters
            # since the first num_group begins with 2
            min_c, min_score = left_cnt + 1, score

    return min_c

def _refined_l_method(num_groups, merge_dist):
    element_cnt = cutoff = last_knee = current_knee = len(num_groups)

    # short circuit, since the l-method doesn't work with the number of elements below 4
    if element_cnt < 4:
        return 1

    while True:
        last_knee = current_knee
        current_knee = _l_method(num_groups[:cutoff], merge_dist[:cutoff])

        # you can keep this number high (* 3), and no problem with that
        # just make sure that the cutoff tends to go down every time
        # but, according to paper this number is 3
        cutoff = current_knee * 3

        if current_knee >= last_knee:
            break

    return current_knee

def get_centroids(X, belong_to):
    clusters_cnt = max(belong_to) + 1
    centroids = [numpy.zeros(len(X[0])) for i in range(clusters_cnt)]
    cluster_member_cnt = [0 for i in range(clusters_cnt)]
    for i, x in enumerate(X):
        belongs = belong_to[i]
        cluster_member_cnt[belongs] += 1
        centroids[belongs] += x
    for i, centroid in enumerate(centroids):
        centroids[i] = centroid / cluster_member_cnt[i]
    return centroids

def get_clusters_cnt(X, method='ward', metric='euclidean'):
    # library: fastcluster
    merge_hist = linkage(X, method=method, metric=metric, preserve_input=True)

    # reorder to be x [2->N]
    num_groups = [i for i in range(2, len(X) + 1)]
    merge_dist = list(reversed([each[2] for each in merge_hist]))

    cluster_count = _refined_l_method(num_groups, merge_dist)

    return cluster_count


class Result:
    def __init__(self, labels, centers):
        self.labels_ = labels
        self.cluster_centers_ = centers

    def predict(self, X):
        ball_tree = BallTree()
        ball_tree.fit(self.cluster_centers_)

        _, indexes = ball_tree.query(X)
        result = []
        for idx, in indexes:
            result.append(self.labels_[idx])

        return result

class DisjointSet:
    def __init__(self, sets_cnt):
        self.level_parent = [i for i in range(2 * sets_cnt - 1)]
        self.highest = sets_cnt

    def parent(self, node):
        if node != self.level_parent[node]:
            self.level_parent[node] = self.parent(self.level_parent[node])
        return self.level_parent[node]

    def join(self, a, b):
        parent_a = self.parent(a)
        parent_b = self.parent(b)

        if a == b:
            raise Exception('joining the same set')

        self.level_parent[parent_a] = self.highest
        self.level_parent[parent_b] = self.highest

        # prevent trees to be tall
        self.parent(a)
        self.parent(b)

        self.highest += 1

    def common(self, a, b):
        return self.parent(a) == self.parent(b)

def agglomerative_l_method(X, method='ward'):
    # library: fastcluster
    merge_hist = linkage(X, method=method, metric='euclidean', preserve_input=True)

    # reorder to be x [2->N]
    num_groups = [i for i in range(2, len(X) + 1)]
    merge_dist = list(reversed([each[2] for each in merge_hist]))

    cluster_count = _refined_l_method(num_groups, merge_dist)

    # print('refined_l_method time:', end_time - start_time)
    # print('cluster_count:', cluster_count)

    # make clusters by merging them according to merge_hist
    disjoint = DisjointSet(len(X))
    for a, b, _, _ in islice(merge_hist, 0, len(X) - cluster_count):
        a, b = int(a), int(b)
        disjoint.join(a, b)

    # get cluster name for each instance
    belong_to = [disjoint.parent(i) for i in range(len(X))]
    # print('belong_to:', belong_to)
    # counter = Counter(belong_to)
    # print('belong_to:', counter)

    # rename the cluster name to be 0 -> cluster_count - 1
    cluster_map = {}
    cluster_name = 0
    belong_to_renamed = []
    for each in belong_to:
        if not each in cluster_map:
            cluster_map[each] = cluster_name
            cluster_name += 1
        belong_to_renamed.append(cluster_map[each])

    # print('belong_to_renamed:', belong_to_renamed)

    centroids = get_centroids(X, belong_to_renamed)
    # print('centroids:', centroids)

    return Result(belong_to_renamed, centroids)