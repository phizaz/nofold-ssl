import unittest
from src import utils
from src.utils.helpers import lengthnorm

class LengtherTest(unittest.TestCase):
    def runTest(self):
        names, points, header = utils.get.get_family_bitscores('RF00014')
        lengther = lengthnorm.Lengther('test_rna', names)
        lengths = utils.get.get_family_lengths('RF00014')

        for name in names:
            length = lengther.length_of(name)
            self.assertEqual(length, lengths[name])

        # recs = utils.get.get_records(utils.path.query_db_path('test_rna'))
        # names = list(map(lambda x: x.name, recs))
        names, _, _ = utils.get.get_query_bitscores('test_rna')
        lengths = utils.get.get_query_lengths_name_variants('test_rna')

        for name in names:
            length = lengther.length_of(name)
            self.assertEqual(length, lengths[name])


class LengthNormalizer(unittest.TestCase):

    def test_length_normalize(self):
        from os.path import join
        names, points, header = utils.get.get_bitscores(join(utils.path.queries_path(), 'rfam75id', 'rfam75id.zNorm.bitscore'))
        points = points[:10]
        print(len(header))

        normalizer = lengthnorm.LengthNormalizer()
        _names, _points, _header = utils.get.get_query_bitscores('rfam75id')
        _points = _points[:10]
        _points = normalizer.length_normalize_full(_names, _points, _header, 'rfam75id')
        self.assertListEqual(names, _names)
        self.assertListEqual(header, _header)

        for pa, pb in zip(points, _points):
            self.assertEqual(len(pa), len(pb))
            for a, b in zip(pa, pb):
                self.assertAlmostEqual(a, b, 2, msg='{} != {} under two decimal places'.format(a, b))
