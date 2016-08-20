import numpy as np


def dist(a, b):
    return np.linalg.norm(a - b)


def avg_dist(points, origin):
    s = 0
    for point in points:
        d = dist(point, origin)
        s += d
    avg_dist = s / len(points)
    return avg_dist


def centroid_of(points):
    points = np.array(points)
    centroid = sum(points) / len(points)
    return centroid


def dist_cluster_min(points_A, points_B):
    from sklearn.neighbors import BallTree
    ballTree = BallTree(points_A)
    d, i = ballTree.query(points_B)
    return float(min(d))


def dist_cluster_avg(points_A, points_B):
    from itertools import product
    import numpy as np
    points_A = np.array(points_A)
    points_B = np.array(points_B)
    s = sum(dist(a, b) for a, b in product(points_A, points_B))
    return s / float(len(points_A) * len(points_B))


def dist_cluster_centroid(points_A, points_B):
    import numpy as np
    points_A = np.array(points_A)
    points_B = np.array(points_B)
    centroid_A = centroid_of(points_A)
    centroid_B = centroid_of(points_B)
    return dist(centroid_A, centroid_B)


class ClosestPoint(object):
    def __init__(self, pivots, names=None):
        self.pivots = pivots
        self.names = names or list(range(len(pivots)))
        from sklearn.neighbors import BallTree
        self.tree = BallTree(self.pivots)

    def closest(self, point):
        points = [point]
        dist, res = self.tree.query(points, k=1, return_distance=True)
        idx = res[0][0]
        return self.names[idx]


class Cluster(object):
    def __init__(self, names, points, name=None):
        self.name = name
        self.names = names
        self.points = points

    def dist_avg(self, cluster):
        assert isinstance(cluster, Cluster)
        return dist_cluster_avg(self.points, cluster.points)

    def dist_min(self, cluster):
        assert isinstance(cluster, Cluster)
        return dist_cluster_min(self.points, cluster.points)

    def dist_centroid(self, cluster):
        assert isinstance(cluster, Cluster)
        return dist_cluster_centroid(self.points, cluster.points)

    def same(self, cluster):
        assert isinstance(cluster, Cluster)
        from utils.short import list_equal
        return list_equal(self.names, cluster.names) and all(
            list_equal(a, b) for a, b in zip(self.points, cluster.points))
