import unittest
import utils
from os.path import join
from utils import *

class SaveQueryRecordsTest(unittest.TestCase):
    query = '_test_save_query_record_'

    def setUp(self):
        import shutil
        try:
            shutil.rmtree(join(utils.path.queries_path(), self.query))
        except: pass

    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(join(utils.path.queries_path(), self.query))
        except: pass

    def runTest(self):
        from Bio import SeqIO

        with open(join(utils.path.queries_path(), 'test_rna', 'test_rna.db')) as handle:
            records = SeqIO.parse(handle, 'fasta')
            records = list(records)


        utils.save.save_query_records(self.query, records)

        with open(join(utils.path.queries_path(), self.query, self.query + '.db')) as handle:
            save_records = SeqIO.parse(handle, 'fasta')
            save_records = list(save_records)

        self.assertEqual(len(records), len(save_records))
        for r, s in zip(records, save_records):
            self.assertEqual(r.name, s.name)
            self.assertEqual(r.seq, s.seq)


class SaveBitscoresTest(unittest.TestCase):
    query = '_test_save_bitscores_'

    def setUp(self):
        import shutil
        try:
            shutil.rmtree(join(utils.path.queries_path(), self.query))
        except:
            pass

    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(join(utils.path.queries_path(), self.query))
        except:
            pass

    def runTest(self):
        names, points, header = utils.get.get_query_bitscores('test_rna')
        utils.save.save_bitscores(self.query, names, points, header)
        _names, _points, _header = utils.get.get_query_bitscores(self.query)
        self.assertListEqual(names, _names)
        self.assertListEqual(points, _points)
        self.assertListEqual(header, _header)
