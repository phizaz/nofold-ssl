import unittest
from src.utils.helpers import cmscore
from src import utils
from os.path import join
import os

os.environ['PATH'] += ':/usr/local/bin'


class CMScoreTest(unittest.TestCase):
    def test_get_cmscore_output(self):
        records = utils.get.get_query_records('test_rna')
        r, total_time = cmscore.get_cmscore_output(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)

        print(r)
        self.assertIsInstance(r, list)
        self.assertTrue(all(isinstance(a, str) for a in r))

    def test_is_valid_cmscore(self):
        records = utils.get.get_query_records('test_rna')
        lines, time = cmscore.get_cmscore_output(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)

        r = cmscore.is_valid_cmscore(lines, records)
        self.assertFalse(r, msg='make sure that names are the same')

        records = utils.get.get_query_records('test_rna')
        records[0].id = records[0].name = 'a'
        records[1].id = records[1].name = 'b'
        lines, time = cmscore.get_cmscore_output(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)

        r = cmscore.is_valid_cmscore(lines, records)
        self.assertTrue(r)

    def test_get_cmname(self):
        records = utils.get.get_query_records('test_rna')
        lines, time = cmscore.get_cmscore_output(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)

        r = cmscore.get_cmname(lines)
        print(r)
        self.assertEqual(r, '5S_rRNA')

    def test_get_cmscore_score(self):
        records = utils.get.get_query_records('test_rna')
        lines, time = cmscore.get_cmscore_output(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)

        r = cmscore.get_cmscore_score(lines)
        print(r)
        self.assertDictEqual(r, {'QRF01739_AESD01000480.1_R': -35.9237, 'QRF01739_AESD01000480.1': -35.9237})

    def test_get_cmscore(self):
        records = utils.get.get_query_records('test_rna')
        records[0].id = records[0].name = 'a'
        records[1].id = records[1].name = 'b'
        cm_name, score, time = cmscore.get_cmscore(join(
            utils.path.cm_path(),
            'RF00001.cm'
        ), records)
        print(cm_name, score)

    def test_get_cmscores(self):
        records = utils.get.get_query_records('test_rna')
        records[0].id = records[0].name = 'a'
        records[1].id = records[1].name = 'b'
        r = cmscore.get_cmscores(records)
        print(r)

    def test_serialize_cmscores(self):
        from collections import OrderedDict
        r = OrderedDict([('a', OrderedDict([('5S_rRNA', -35.9237), ('5_8S_rRNA', -52.1632)])),
                         ('b', OrderedDict([('5S_rRNA', -35.9237), ('5_8S_rRNA', -52.1632)]))])

        s = cmscore.serialize_cmscores(r)
        print(s)
        self.assertEqual(s, '5S_rRNA\t5_8S_rRNA\na\t-35.9237\t-52.1632\nb\t-35.9237\t-52.1632\n')

    def test_save_cmscores(self):
        from collections import OrderedDict
        r = OrderedDict([('a', OrderedDict([('5S_rRNA', -35.9237), ('5_8S_rRNA', -52.1632)])),
                         ('b', OrderedDict([('5S_rRNA', -35.9237), ('5_8S_rRNA', -52.1632)]))])
        cmscore.save_cmscores(r, join(
            utils.path.tmp_path(), 'cmscore.bitscore'
        ))
        from os.path import exists
        self.assertTrue(exists(join(utils.path.tmp_path(), 'cmscore.bitscore')))
        from os import remove
        remove(join(utils.path.tmp_path(), 'cmscore.bitscore'))


