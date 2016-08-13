import unittest

import utils
from os.path import join

class GetTest(unittest.TestCase):

    def test_get_all_families(self):
        families = utils.get.get_all_families()
        print(families)
        self.assertTrue(all(fam[:2] == 'RF' for fam in families))
        self.assertEqual(len(families), 1972)

    def test_get_calculated_families(self):
        families = utils.get.get_calculated_families()
        print(families)
        self.assertTrue(all(fam[:2] == 'RF' for fam in families))
        self.assertGreaterEqual(len(families), 1939)

    def test_get_records_and_cnt(self):
        supplies_path = join(utils.path.src_path(), 'tests', 'supplies', 'check_bitscore')
        db_file = join(supplies_path, 'RF00014.db')

        records = utils.get.get_records(db_file)
        print(records)
        from Bio.SeqRecord import SeqRecord
        self.assertTrue(all(isinstance(rec, SeqRecord) for rec in records))
        self.assertEqual(len(records), 5)

        cnt = utils.get.get_record_count(db_file)
        self.assertEqual(cnt, 5)

    def test_get_query_records(self):
        records = utils.get.get_query_records('test_rna')
        print(records)
        from Bio.SeqRecord import SeqRecord
        self.assertTrue(all(isinstance(rec, SeqRecord) for rec in records))
        self.assertEqual(len(records), 2)

    def test_get_query_families(self):
        families = utils.get.get_query_families('fam40_typedistributed')
        print(len(families))
        self.assertTrue(all(fam[:2] == 'RF' for fam in families))
        self.assertEqual(len(families), 40)

    def test_get_bitscores(self):
        supplies_path = join(utils.path.src_path(), 'tests', 'supplies', 'check_bitscore')
        bitscore_file = join(supplies_path, 'RF00014.bitscore')
        names, points, header = utils.get.get_bitscores(bitscore_file)
        print(len(names))
        print(len(points))
        print(len(header))

        self.assertEqual(len(names), 5)
        self.assertTrue(all(name[:2] == 'RF' for name in names))
        self.assertEqual(len(points), 5)
        self.assertEqual(len(header), 1973)

    def test_get_query_bitscores(self):
        names, points, header = utils.get.get_query_bitscores('test_rna')
        print(len(names))
        print(len(points))
        print(len(header))

        self.assertEqual(len(names), 2)
        self.assertEqual(len(points), 2)
        self.assertEqual(len(header), 1973)