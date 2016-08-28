import unittest
import utils
from normalize_bitscore import length_normalize, pca, znormalize, run


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

    def test_run(self):
        from os.path import join
        bitscore_file = join(utils.path.results_path(), 'combined.novel-1-2-3hp.bitscore')
        names, points, header = utils.get.get_bitscores(bitscore_file)
        query = 'novel-1-2-3hp'
        components = 100

        l_names, l_points, l_header = run(names, points, header, query, components, True)
        nl_names, nl_points, nl_header = run(names, points, header, query, components, False)

        self.assertListEqual(l_names, nl_names)

        def almost_equal(a, b):
            return abs(a - b) < 1e-3

        def list_not_equal(l1, l2):
            return any(not almost_equal(a, b) for a, b in zip(l1, l2))


        self.assertEqual(len(l_points), len(nl_points))
        for l_point, nl_point in zip(l_points, nl_points):
            self.assertTrue(list_not_equal(l_point, nl_point), msg='normalization has no effect ! {} = {}'.format(l_point, nl_point))

        self.assertListEqual(l_header, nl_header)

        print(l_points[0])
        print(nl_points[0])


    def test_real(self):
        from os.path import join
        from os import remove
        from os.path import exists

        query = 'novel-1-2-3hp'
        tag = 'novel-1-2-3hp'

        if not exists(join(utils.path.results_path(), 'combined.{}.bitscore'.format(tag))):
            utils.run.run_python_attach_output(join(utils.path.src_path(), 'combine_rfam_bitscore.py'),
                                               '--unformatted',
                                               query=query,
                                               nn=13)

        file = join(utils.path.results_path(), 'combined.{}.normalized.bitscore'.format(tag))
        if exists(file):
            remove(file)

        utils.run.run_python_attach_output(join(utils.path.src_path(), 'normalize_bitscore.py'),
                                           '--lengthnorm',
                                           tag=tag,
                                           query=query,
                                           components=100)

        self.assertTrue(exists(file), 'file {} not found'.format(file))

    def test_real_large(self):
        from os.path import join
        from os import remove
        from os.path import exists

        query = 'rfam75id-rename'
        tag = 'rfam75id-rename.cripple0'

        if not exists(join(utils.path.results_path(), 'combined.{}.bitscore'.format(tag))):
            utils.run.run_python_attach_output(join(utils.path.src_path(), 'combine_rfam_bitscore.py'),
                                               query=query,
                                               cripple=0,
                                               nn=7)

        file = join(utils.path.results_path(), 'combined.{}.normalized.bitscore'.format(tag))
        if exists(file):
            remove(file)

        utils.run.run_python_attach_output(join(utils.path.src_path(), 'normalize_bitscore.py'),
                                           '--lengthnorm',
                                           tag=tag,
                                           query=query,
                                           components=100)

        self.assertTrue(exists(file))
