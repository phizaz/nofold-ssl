import unittest
from src import utils
from src.utils.helpers import space
import numpy as np

class SpaceTest(unittest.TestCase):

    def test_dist(self):
        a = np.array([0,0])
        b = np.array([3,4])
        self.assertAlmostEqual(space.dist(a, b), 5)

    def test_avg_dist(self):
        pivot = 1
        points = [1,2,3]
        self.assertAlmostEqual(space.avg_dist(points, pivot), 1.0)

    def test_centroid_of(self):
        points = [1,2,3]
        self.assertAlmostEqual(space.centroid_of(points), 2.0)

    def test_dist_cluster_min(self):
        a = [
            [1,1], [2,2]
        ]
        b = [
            [2,2], [3,3]
        ]
        self.assertAlmostEqual(space.dist_cluster_min(a, b), 0)

    def test_dist_cluster_avg(self):
        a = [
            [1, 1], [2, 2]
        ]
        b = [
            [2, 2], [3, 3]
        ]
        self.assertAlmostEqual(space.dist_cluster_avg(a, b), 1.41421356)

    def test_dist_cluster_avg_fast(self):
        a = [
            [1, 1], [2, 2]
        ]
        b = [
            [2, 2], [3, 3]
        ]
        self.assertAlmostEqual(space.dist_cluster_avg_fast(a, b), 1.41421356)

    def test_dist_cluster_avg_speed(self):
        a = np.random.rand(500, 100)
        b = np.random.rand(500, 100)

        def time_it(fn):
            def wrapper():
                import time
                start = time.time()
                res = fn()
                end = time.time()
                print('time elapsed:', end - start)
                return res

            return wrapper

        @time_it
        def run_normal():
            return space.dist_cluster_avg(a, b)

        @time_it
        def run_fast():
            return space.dist_cluster_avg_fast(a, b)

        aa = run_normal()
        bb = run_fast()
        self.assertAlmostEqual(aa, bb)

    def test_dist_cluster_centroid(self):
        a = [
            [0,0],[0,2]
        ]
        b = [
            [1,0],[1,2]
        ]
        self.assertAlmostEqual(space.dist_cluster_centroid(a, b), 1.0)

class ClosestPointTest(unittest.TestCase):

    def test_closest(self):
        points = [
            [1,1], [2,2], [3,3]
        ]
        closest = utils.helpers.space.ClosestPoint(points)
        res = closest.closest([0,0])
        self.assertEqual(res, 0)
        res = closest.closest([3,3])
        self.assertEqual(res, 2)

    def test_names(self):
        points = [
            [1,1], [2,2]
        ]
        names = ['a', 'b']
        closest = utils.helpers.space.ClosestPoint(points, names)
        res = closest.closest([2,2])
        self.assertEqual(res, 'b')
        res = closest.closest([0,0])
        self.assertEqual(res, 'a')

class ClusterTest(unittest.TestCase):

    def test_dist_avg(self):
        A = utils.helpers.space.Cluster(['a', 'b'], [
            [0, -1], [0, 3]
        ])
        B = utils.helpers.space.Cluster(['c', 'd'], [
            [1, 0], [1, 2]
        ])
        dist = A.dist_avg(B)
        self.assertAlmostEqual(dist, 2.288245611270)

    def test_dist_min(self):
        A = utils.helpers.space.Cluster(['a', 'b'], [
            [0, -1], [0, 3]
        ])
        B = utils.helpers.space.Cluster(['c', 'd'], [
            [1, 0], [1, 2]
        ])
        dist = A.dist_min(B)
        self.assertAlmostEqual(dist, 1.414213562)

    def test_dist_centroid(self):
        A = utils.helpers.space.Cluster(['a', 'b'], [
            [0, -1], [0, 3]
        ])
        B = utils.helpers.space.Cluster(['c', 'd'], [
            [1, 0], [1, 2]
        ])
        dist = A.dist_centroid(B)
        self.assertAlmostEqual(dist, 1.0)

    def test_same(self):
        A = utils.helpers.space.Cluster(['a', 'b'], [
            [0, -1], [0, 3]
        ])
        B = utils.helpers.space.Cluster(['c', 'd'], [
            [1, 0], [1, 2]
        ])
        C = utils.helpers.space.Cluster(['a', 'b'], [
            [0, -1], [0, 3]
        ])
        self.assertFalse(A.same(B))
        self.assertTrue(A.same(C))
