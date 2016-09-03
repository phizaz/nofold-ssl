import unittest
from src import utils
from os.path import join


class SaveQueryRecordsTest(unittest.TestCase):
    query = '_test_save_query_record_'

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


class SaveQueryBitscoresTest(unittest.TestCase):
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
        utils.save.save_query_bitscores(self.query, names, points, header)
        _names, _points, _header = utils.get.get_query_bitscores(self.query)
        self.assertListEqual(names, _names)
        self.assertListEqual(points, _points)
        self.assertListEqual(header, _header)


class SaveClustersTest(unittest.TestCase):
    file = join(utils.path.results_path(), 'test_save_clusters.clusters')

    def setUp(self):
        import os
        try:
            os.remove(self.file)
        except:
            pass

    def tearDown(self):
        import os
        try:
            os.remove(self.file)
        except:
            pass

    def test_labeless_clusters(self):
        clusters = [
            ['A', 'B', 'C'],
            ['D', 'E'],
            ['F']
        ]
        utils.save.save_name_clusters(self.file, clusters)

        self.assertListEqual(utils.get.get_name_clusters(self.file), clusters)

    def test_label_clusters(self):
        clusters = dict(
            a=['A', 'B', 'C'],
            b=['D', 'E']
        )
        utils.save.save_name_clusters(self.file, clusters)
        self.assertListEqual(utils.get.get_name_clusters(self.file), [
            ['A', 'B', 'C'],
            ['D', 'E']
        ])

    def test_save_clusters(self):
        from utils.helpers import space
        A = [
            space.Cluster(['a', 'b'], [
                [0, 0], [1, 1]
            ]),
            space.Cluster(['c'], [
                [2, 2]
            ])
        ]
        utils.save.save_clusters(self.file, A)
        self.assertListEqual(utils.get.get_name_clusters(self.file), [
            ['a', 'b'],
            ['c']
        ])

    def test_save_csv(self):
        utils.save.save_csv(
            ['a', 'b'],
            [[1,2], [3,4]],
            join(utils.path.results_path(), 'test_save_csv.csv')
        )

