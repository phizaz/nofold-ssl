import unittest
from src.combine_rfam_bitscore import run


class CombineRfamBitscore(unittest.TestCase):
    def test_run(self):
        names, points, header = run('test_rna', False, 1, 2)
        self.assertEqual(len(header), 1973)
        for each in points:
            self.assertEqual(len(each), 1973)

    def test_real(self):
        import utils
        from os.path import join
        output = utils.run.run_python_attach_output(join(utils.path.src_path(), 'combine_rfam_bitscore.py'),
                                                    query='test_rna',
                                                    cripple=1,
                                                    nn=2)
        print(output)

        _names, _points, _header = utils.get.get_bitscores(
            join(utils.path.results_path(), 'combined.test_rna.cripple1.bitscore'))

        names, points, header = run('test_rna', False, 1, 2)
        self.assertEqual(len(header), 1973)
        for each in points:
            self.assertEqual(len(each), 1973)

        self.assertListEqual(names, _names)
        self.assertListEqual(points, _points)
        self.assertListEqual(header, _header)
