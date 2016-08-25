from clustering import run
import unittest
import utils

class ClusterSemiLabelPropagation(unittest.TestCase):


    def test_run(self):

        from os.path import join

        file = join(utils.path.results_path(), 'combined.novel-1-2-3hp.zNorm.pcNorm100.zNorm.bitscore')
        seed_names, seed_points, query_names, query_points, header = utils.get.get_seed_query_bitscore(file)
        clusters = run(seed_names, seed_points, query_names, query_points, 'labelSpreading', 'rbf', 1.0, None, 0.5)
        self.assertTrue(2 <= len(clusters), msg='clustering quality is too bad {}'.format(len(clusters)))
        from utils.helpers import space
        for cluster in clusters:
            self.assertIsInstance(cluster, space.Cluster)
            for name in cluster.names:
                self.assertTrue('novel' in name, msg='should cluster only the query')

    def test_real(self):
        from os.path import join
        utils.run.run_python_attach_output(join(utils.path.src_path(), 'clustering.py'),
                                           '--lengthnorm',
                                           tag='novel-1-2-3hp',
                                           alg='labelSpreading',
                                           kernel='rbf',
                                           gamma=0.5,
                                           alpha=1.0)

        clusters = utils.get.get_name_clusters(join(utils.path.results_path(), 'combined.novel-1-2-3hp.labelSpreading.cluster'))
        self.assertTrue(2 <= len(clusters), msg='clustering quality is too bad')
        for names in clusters:
            for name in names:
                self.assertTrue('novel' in name, msg='should cluster only the query')

    def test_real_large(self):
        from os.path import join
        utils.run.run_python_attach_output(join(utils.path.src_path(), 'clustering.py'),
                                           '--lengthnorm',
                                           tag='rfam75id-rename.cripple0',
                                           alg='labelSpreading',
                                           kernel='rbf',
                                           gamma=0.5,
                                           alpha=1)

        clusters = utils.get.get_name_clusters(
            join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.cluster'))
        self.assertTrue(18 <= len(clusters) <= 30, msg='clustering quality is too bad')

