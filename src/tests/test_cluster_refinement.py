import unittest
import utils
from cluster_refinement import *


class ClusterRefinementTest(unittest.TestCase):
    def test_split_cluster(self):
        import utils.helpers.space as space
        A = space.Cluster([
            'a', 'b'
        ], [
            [0, 0], [1, 1]
        ])

        B = space.Cluster([
            'c'
        ], [
            [0, 1]
        ])

        C = space.Cluster([
            'd'
        ], [
            [3, 3]
        ])

        splitted = split_cluster(A, [A, B, C], 1.0)
        print(splitted)
        self.assertEqual(len(splitted), 2)
        splitted.sort(key=lambda x: x.names[0])
        self.assertListEqual(splitted[0].names, ['a'])
        self.assertListEqual(splitted[1].names, ['b'])
        self.assertListEqual(splitted[0].points, [[0,0]])
        self.assertListEqual(splitted[1].points, [[1,1]])

    def test_split_clusters(self):
        from utils.helpers import space
        A = space.Cluster([
            'a', 'b'
        ], [
            [0, 0], [1, 1]
        ])

        B = space.Cluster([
            'c'
        ], [
            [0, 1]
        ])

        C = space.Cluster([
            'd'
        ], [
            [3, 3]
        ])

        splitted = split_clusters([A, B, C], 1.0)
        splitted.sort(key=lambda x: x.names[0])
        for each in splitted:
            print(each.__dict__)

        def clust_equal(a, b):
            self.assertListEqual(a.names, b.names)
            self.assertListEqual(a.points, b.points)
            self.assertEqual(a.name, b.name)

        clust_equal(splitted[0], space.Cluster(['a'], [[0,0]]))
        clust_equal(splitted[1], space.Cluster(['b'], [[1,1]]))
        clust_equal(splitted[2], B)
        clust_equal(splitted[3], C)

    def test_merge_clusters(self):
        from os.path import join
        clusters = utils.get.get_clusters(join(
            utils.path.results_path(),
            'combined.novel-1-2-3hp.cripple3.labelSpreading.cluster'
        ), join(
            utils.path.results_path(),
            'combined.novel-1-2-3hp.cripple3.zNorm.pcNorm100.zNorm.bitscore'
        ))
        print(clusters)
        for clust in clusters:
            print(clust.names)

        score_file = join(utils.path.results_path(), 'combined.novel-1-2-3hp.cripple3.zNorm.pcNorm100.zNorm.bitscore')
        seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(score_file)
        # get seed clusters
        seed_groups = utils.modify.group_bitscore_by_family(seed_names, seed_points)
        # print('seed_groups:', seed_groups)

        print('calculating centroids for seed clusters..')
        seed_centroids = {}
        from utils.helpers import space
        for fam, points in seed_groups.items():
            seed_centroids[fam] = space.centroid_of(points)
        # print('seed_centroids:', seed_centroids)

        names = []
        points = []
        for key, val in seed_centroids.items():
            names.append(key)
            points.append(val)

        # closest_seed_centroid = space.ClosestPoint(seed_centroids.values(), seed_centroids.keys())
        closest_seed_centroid = space.ClosestPoint(points, names)
        print(closest_seed_centroid.names)

        merged_clusters = merge_clusters(closest_seed_centroid, clusters)

        count = sum(len(clust.names) for clust in clusters)

        self.assertIsInstance(merged_clusters, list)
        for clust in merged_clusters:
            self.assertIsInstance(clust, space.Cluster)

        _count = sum(len(clust.names) for clust in merged_clusters)
        __count = sum(len(clust.points) for clust in merged_clusters)
        self.assertEqual(count, _count)
        self.assertEqual(count, __count)

    def test_identical_clusters(self):
        from utils.helpers import space
        A = [
            space.Cluster(['a', 'b'], [
                [0, 0], [1,1]
            ]),
            space.Cluster(['c'], [
                [2,2]
            ])
        ]
        B = [
            space.Cluster(['a', 'b'], [
                [0, 0], [1, 1]
            ]),
            space.Cluster(['d'], [
                [2, 2]
            ])
        ]
        C = [
            space.Cluster(['c'], [
                [2, 2]
            ]),
            space.Cluster(['b', 'a'], [
                [1,1], [0,0]
            ]),
        ]
        D = [
            space.Cluster(['c'], [
                [2, 2]
            ]),
            space.Cluster(['b', 'a'], [
                [1, 1], [0, 0]
            ]),
            space.Cluster(['d'], [
                [3,3]
            ])
        ]
        self.assertFalse(identical_clusters(A, B))
        self.assertTrue(identical_clusters(A, C))
        self.assertFalse(identical_clusters(A, D))

    def test_real(self):
        from os.path import join
        utils.run.run_python_attach_output(
            join(utils.path.src_path(), 'cluster_refinement.py'),
            '--lengthnorm',
            tag='novel-1-2-3hp',
            alg='labelSpreading',
            C=1.0,
        )

    def test_real_large(self):
        from os.path import join
        utils.run.run_python_attach_output(
            join(utils.path.src_path(), 'cluster_refinement.py'),
            '--lengthnorm',
            tag='rfam75id-rename.cripple0',
            alg='labelSpreading',
            C=1.2
        )

