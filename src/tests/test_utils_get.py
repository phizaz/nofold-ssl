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

    def test_get_sequences(self):
        seqs = utils.get.get_sequences(join(utils.path.src_path(), 'tests', 'supplies', 'check_bitscore', 'RF00014.db'))
        self.assertEqual(len(seqs), 5)
        for each in seqs:
            self.assertIsInstance(each, str)

    def test_get_query_records(self):
        records = utils.get.get_query_records('test_rna')
        print(records)
        from Bio.SeqRecord import SeqRecord
        self.assertTrue(all(isinstance(rec, SeqRecord) for rec in records))
        self.assertEqual(len(records), 2)

    def test_get_query_sequences(self):
        seqs = utils.get.get_query_sequences('test_rna')
        self.assertEqual(len(seqs), 2)
        for each in seqs:
            self.assertIsInstance(each, str)

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

    def test_get_family_sequences(self):
        seqs = utils.get.get_family_sequences('RF00014')
        self.assertEqual(len(seqs), 5)
        for each in seqs:
            self.assertIsInstance(each, str)

    def test_get_family_records(self):
        records = utils.get.get_family_records('RF00014')
        self.assertEqual(len(records), 5)
        for each in records:
            self.assertTrue(hasattr(each, 'name'))
            self.assertTrue(hasattr(each, 'seq'))

    def test_get_family_bitscores(self):
        names, points, header = utils.get.get_family_bitscores('RF00014')
        self.assertEqual(len(names), 5)
        self.assertEqual(len(points), 5)
        self.assertEqual(len(header), 1973)

    def test_get_family_header_string(self):
        header = utils.get.get_family_header_string('RF00001')
        self.assertEqual(len(header.split()), 1973)

    def test_get_family_header(self):
        header = utils.get.get_family_header('RF00001')
        self.assertEqual(len(header), 1973)

    def test_get_knearest_points_given_a(self):
        a_points = [
            [1, 1], [10, 10]
        ]
        target_points = [
            [2, 2], [0, 0], [8, 8], [9, 9]
        ]

        target_names = ['t', 'tt', 'ttt', 'tttt']
        results = utils.get.get_knearest_points_given_a(2, a_points, target_names, target_points)
        self.assertEqual(len(results), len(a_points))
        for each in results:
            self.assertEqual(len(each), 2)
            for dist, name, point in each:
                self.assertIn(name, target_names)
                self.assertIn(point, target_points)

        self.assertSetEqual(set(map(lambda x: x[1], results[0])), set(target_names[:2]))
        self.assertSetEqual(set(map(lambda x: x[1], results[1])), set(target_names[2:]))

    def test_get_knearest_seed_given_query(self):
        query_names, query_points, query_header = utils.get.get_query_bitscores('test_rna')
        results = utils.get.get_knearest_seed_given_query(3, query_header, query_points)

        print(results)

        self.assertEqual(len(results), 2)
        for each in results:
            self.assertEqual(len(each), 3)

    def test_get_family_lengths(self):
        lengths = utils.get.get_family_lengths('RF00014')
        print(lengths)
        self.assertDictEqual(lengths, {'RF00014_CP000468.1': 87, 'RF00014_AE005674.1': 87, 'RF00014_M15749.1': 85,
                                       'RF00014_CP000653.1': 85, 'RF00014_CP000857.1': 84})

    def test_get_query_lengths(self):
        lengths = utils.get.get_query_lengths('test_rna')
        print(lengths)
        self.assertDictEqual(lengths, {'QRF01739_AESD01000480.1_RNA': 61, 'QRF01739_AESD01000480.1': 61})

    def test_get_name_variations(self):
        db_file = utils.path.query_db_path('test_rna')
        bitscore_file = utils.path.query_bitscore_path('test_rna')
        name_variants = utils.get.get_names_variants(db_file, bitscore_file)
        print(name_variants)
        self.assertListEqual(name_variants, [['QRF01739_AESD01000480.1'],
                                             ['QRF01739_AESD01000480.1_RNA', 'QRF01739_AESD01000480.1_R']])

    def test_get_lengths_name_variants(self):
        db_file = utils.path.query_db_path('test_rna')
        bitscore_file = utils.path.query_bitscore_path('test_rna')
        names, _, _ = utils.get.get_query_bitscores('test_rna')
        lengths = utils.get.get_lengths_name_variants(db_file, bitscore_file)
        for name in names:
            self.assertEqual(lengths[name], 61)

    def test_get_query_lengths_name_variants(self):
        lengths = utils.get.get_query_lengths_name_variants('test_rna')
        names, _, _ = utils.get.get_query_bitscores('test_rna')
        for name in names:
            print(name)
            self.assertEqual(lengths[name], 61)

        lengths = utils.get.get_query_lengths_name_variants('novel-1-2-3hp')
        _lengths = utils.get.get_query_lengths('novel-1-2-3hp')
        for key, val in _lengths.items():
            self.assertEqual(lengths[key], val)

    def test_get_family_lengths_name_variants(self):
        lengths = utils.get.get_family_lengths_name_variants('RF00014')
        _lengths = utils.get.get_family_lengths('RF00014')

        for key, val in _lengths.items():
            self.assertEqual(lengths[key], val)
