import unittest
import utils
from pca_normalize_bitscore import length_normalize, pca, znormalize


class PCANormalizeBitscoreTest(unittest.TestCase):
    def test_length_normalize(self):
        names, points, header = utils.get.get_query_bitscores('novel-1-2-3hp')
        points = length_normalize(names, points, header, 'novel-1-2-3hp')
        print(len(points))

    def test_pca(self):
        names, points, header = utils.get.get_query_bitscores('novel-1-2-3hp')
        _points, _header = pca(100, points)
        self.assertEqual(len(points), len(_points))
        self.assertEqual(len(_header), 100)

        for each in _points:
            self.assertEqual(len(each), 100)

    def test_znormalize(self):
        points = [
            [-100, 100, 50],
            [-300, 0, 20],
            [0, 0, 0]
        ]

        import numpy as np

        points = np.array(points)

        points = znormalize(points)
        self.assertEqual(len(points), 3)
        for point in points:
            self.assertEqual(len(point), 3)
            for each in point:
                self.assertTrue(-2 < each < 2)

    def test_real(self):
        from os.path import join
        from os import remove
        from os.path import exists

        query = 'novel-1-2-3hp'
        tag = 'novel-1-2-3hp.cripple3'

        if not exists(join(utils.path.results_path(), 'combined.{}.bitscore'.format(tag))):
            utils.run.run_python_attach_output(join(utils.path.src_path(), 'combine_rfam_bitscore.py'),
                                               query=query,
                                               cripple=3,
                                               nn=3)

        files = [
            join(utils.path.results_path(), 'combined.{}.zNorm.bitscore'.format(tag)),
            join(utils.path.results_path(), 'combined.{}.zNorm.pcNorm100.bitscore'.format(tag)),
            join(utils.path.results_path(), 'combined.{}.zNorm.pcNorm100.zNorm.bitscore'.format(tag))
        ]

        for file in files:
            if exists(file):
                remove(file)

        utils.run.run_python_attach_output(join(utils.path.src_path(), 'pca_normalize_bitscore.py'),
                                           '--lengthnorm',
                                           tag=tag,
                                           query=query,
                                           components=100)

        for file in files:
            self.assertTrue(exists(file))
