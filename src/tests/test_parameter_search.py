import unittest
from parameter_search import *


class ParameterSearchTest(unittest.TestCase):
    def test_run_combine(self):
        query = 'rfam75id-rename'
        cripple = 0
        nn_seed = 3
        names, points, header = run_combine(query, cripple, nn_seed)
        print(len(names))
        print(len(points))
        print(len(header))
        self.assertEqual(len(names), len(points))
        self.assertEqual(len(names), 4877)
        self.assertEqual(len(header), 1929)

    def test_run_normalized(self):
        import utils
        from os.path import join
        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.bitscore')
        names, points, header = utils.get.get_bitscores(path)
        names, points, header = run_normalize(names, points, header, 'rfam75id-rename', True)
        print(len(names))
        print(len(points))
        print(len(header))
        self.assertEqual(len(header), 100)

    def test_run_clustering(self):
        import utils
        from os.path import join
        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.zNorm.pcNorm100.zNorm.bitscore')
        names, points, header = utils.get.get_bitscores(path)
        clusters = run_clustering(names, points, header, 'labelSpreading', 'rbf', 0.5, 1.0)
        from utils.helpers import space
        for cluster in clusters:
            self.assertIn(cluster, space.Cluster)
        print(len(clusters))

    def test_run_cluster_refinement(self):
        import utils
        from os.path import join
        point_file = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.zNorm.pcNorm100.zNorm.bitscore')
        names, points, header = utils.get.get_bitscores(point_file)

        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.cluster')
        clusters = utils.get.get_clusters(path, point_file)

        clusters = run_cluster_refinement(clusters, names, points, header, 1.0)
        print(len(clusters))

    def test_run_evaluate(self):
        import utils
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


