import unittest

import utils
from os.path import join

class CheckTest(unittest.TestCase):

    def test_check_bit_score(self):
        supplies_path = join(utils.path.src_path(), 'tests', 'supplies', 'check_bitscore')
        correct_bitscore = join(supplies_path, 'RF00014.bitscore')
        db_file = join(supplies_path, 'RF00014.db')

        self.assertTrue(utils.check.check_bitscore(correct_bitscore, db_file))

        wrong_bitscore = join(supplies_path, 'RF00014_wrong_cell_missing.bitscore')
        self.assertFalse(utils.check.check_bitscore(wrong_bitscore, db_file))

        wrong_bitscore = join(supplies_path, 'RF00014_wrong_cell_missing.bitscore')
        self.assertFalse(utils.check.check_bitscore(wrong_bitscore, db_file, strict=False))

        wrong_bitscore = join(supplies_path, 'RF00014_wrong_row_missing.bitscore')
        self.assertFalse(utils.check.check_bitscore(wrong_bitscore, db_file))

    def test_check_query(self):
        self.assertTrue(utils.check.check_query('test_rna', strict=False))
        self.assertTrue(utils.check.check_query('test_rna', strict=True))

    def test_check_family(self):
        self.assertTrue(utils.check.check_family('RF00014'))