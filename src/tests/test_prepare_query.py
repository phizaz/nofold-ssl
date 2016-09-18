from __future__ import print_function
import unittest
from src import utils
from src import prepare_query


class PrepareQueryTest(unittest.TestCase):
    def test_create_name(self):
        name = prepare_query.create_name('RF00001', 10)
        print(name)
        self.assertEqual(name, 'RF00001_000010')

    def test_short_name_formatted(self):
        name = 'RF00001_ABCDOGEDURODERUDO'
        running_no = 10
        new_name = prepare_query.short_name_formatted(name, running_no)
        print(new_name)
        self.assertEqual(new_name, 'RF00001_000010')

    def test_short_name_unformatted(self):
        name = 'SOMENONSENSNAME'
        running_no = 10
        query = 'lncRNA'
        new_name = prepare_query.short_name_unformatted(name, running_no, query)
        print(new_name)
        self.assertEqual(new_name, 'lncRNA_000010')

    def test_shorten_names(self):
        query = 'gencode.v25.lncRNA'
        records = utils.get.get_query_records(query)
        names = [
            rec.name
            for rec in records
            ]
        formatted = False
        new_names, new_to_old = prepare_query.shorten_names(names, query, formatted)
        print(new_names[0])
        print(new_to_old[new_names[0]])
        self.assertEqual(len(new_names), len(new_to_old))
        self.assertEqual(len(new_names), len(names))
        self.assertEqual(new_names[0], 'gencode.v25.lncRNA_000001')
        self.assertEqual(new_to_old[new_names[0]],
                         'ENST00000473358.1|ENSG00000243485.4|OTTHUMG00000000959.2|OTTHUMT00000002840.1|MIR1302-2-001|MIR1302-2|712|')

    def test_rename(self):
        query = 'gencode.v25.lncRNA'
        records = utils.get.get_query_records(query)
        formatted = False
        new_records, new_to_old = prepare_query.rename(records, query, formatted)
        print(new_records[0])
        self.assertEqual(len(new_records), len(new_to_old))
        self.assertEqual(len(new_records), len(records))
        self.assertEqual(new_records[0].name, 'gencode.v25.lncRNA_000001')
        self.assertEqual(new_to_old[new_records[0].name],
                         'ENST00000473358.1|ENSG00000243485.4|OTTHUMG00000000959.2|OTTHUMT00000002840.1|MIR1302-2-001|MIR1302-2|712|')

    def test_run_rename(self):
        query = 'gencode.v25.lncRNA'
        formatted = False
        new_records, new_to_old, new_query = prepare_query.run_rename(query, formatted)
        _new_records = utils.get.get_query_records(new_query)

        for a, b in zip(new_records, _new_records):
            self.assertEqual(a.name, b.name)
            self.assertEqual(a.id, b.id)
            self.assertEqual(a.seq, b.seq)

        _new_to_old = prepare_query.read_new_to_old(new_query)
        self.assertDictEqual(new_to_old, _new_to_old)

    def test_run_cmscore(self):
        import os
        os.environ['PATH'] += ':/usr/local/bin'
        query = 'test_rna'
        cpu = None
        _, _, new_query = prepare_query.run_rename(query, True)
        cmscores = prepare_query.run_cmscore(new_query, cpu)

        from src import utils
        names, points, header = utils.get.get_query_bitscores(new_query)
        self.assertEqual(len(names), 2)
        self.assertEqual(len(points), 2)
        self.assertEqual(len(header), 1973)




