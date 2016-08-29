import unittest
from src.parameter_search import *
from src import utils


class ParameterSearchTest(unittest.TestCase):
    def test_run_combine(self):
        query = 'rfam75id-rename'
        cripple = 0
        nn_seed = 3
        names, points, header = run_combine(query, False, cripple, nn_seed, False)
        print(len(names))
        print(len(points))
        print(len(header))
        self.assertEqual(len(names), len(points))
        self.assertEqual(len(names), 4877)
        self.assertEqual(len(header), 1929)

    def test_run_normalized(self):
        from os.path import join
        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.bitscore')
        names, points, header = utils.get.get_bitscores(path)

        def almost_equal(a, b):
            return abs(a - b) < 1e-3

        self.assertTrue(almost_equal(1, 1.0001))
        self.assertFalse(almost_equal(1, 1.1))

        def list_not_equal(l1, l2):
            return any(not almost_equal(a, b) for a, b in zip(l1, l2))

        self.assertTrue(list_not_equal([1,2,3], [1,2,4]))
        self.assertFalse(list_not_equal([1,2,3], [1,2,3]))
        self.assertFalse(list_not_equal([1.0001, 2.0001], [0.9999, 1.99999]))

        query = 'rfam75id-rename'
        l_names, l_points, l_header = run_normalize(names, points, header, query, True)
        nl_names, nl_points, nl_header = run_normalize(names, points, header, query, False)

        self.assertListEqual(l_names, nl_names)

        self.assertEqual(len(l_points), len(nl_points))
        for l_point, nl_point in zip(l_points, nl_points):
            self.assertTrue(list_not_equal(l_point, nl_point), msg='normalization has no effect ! {} = {}'.format(l_point, nl_point))

        self.assertListEqual(l_header, nl_header)

        print(l_points[0])
        print(nl_points[0])

    def test_run_clustering(self):
        from os.path import join
        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.normalized.bitscore')
        names, points, header = utils.get.get_bitscores(path)
        clusters = run_clustering(names, points, header, 'labelSpreading', 'rbf', 0.5, 1.0)
        from src.utils.helpers import space
        for cluster in clusters:
            self.assertIsInstance(cluster, space.Cluster)
        print(len(clusters))

    def test_run_cluster_refinement(self):
        from os.path import join
        point_file = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.normalized.bitscore')
        names, points, header = utils.get.get_bitscores(point_file)

        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.cluster')
        clusters = utils.get.get_clusters(path, point_file)

        clusters = run_cluster_refinement(clusters, names, points, header, 1.0)
        print(len(clusters))

    def test_run_evaluate(self):
        from os.path import join
        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.refined.cluster')
        clusters = utils.get.get_name_clusters(path)
        names = [
            rec.name
            for rec in utils.get.get_query_records('rfam75id-rename')
            if not utils.short.is_bg(rec.name)
        ]

        average = run_evaluate(clusters, names)
        print(average)

        self.assertAlmostEqual(average['sensitivity'], 1.0)
        self.assertAlmostEqual(average['precision'], 1.0)
        self.assertGreater(average['max_in_cluster'], 0.8)

    def test_save(self):
        args = ['a', 'b', 'c']
        results = {
            (1,2,3): {
                'sensitivity': 4,
                'precision': 5,
                'max_in_cluster': 6
            }
        }
        cols, rows = save(args, results)
        self.assertListEqual(cols, ['a', 'b', 'c', 'sensitivity', 'precision', 'max_in_cluster'])
        self.assertListEqual(rows, [(1, 2, 3, 4, 5, 6)])


