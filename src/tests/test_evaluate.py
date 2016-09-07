import unittest
from src.evaluate import *
from src import utils

clusters = [
    ['RF01_A', 'RF01_B', 'RF02_C', 'bg001', 'bg002'],
    ['RF02_D', 'bg003'],
    ['RF01_E', 'RF01_F', 'bg004'],
    ['bg005', 'bg006']
]

from collections import defaultdict

names_by_family = defaultdict(list)
names = []
from itertools import chain

for each in chain(*clusters):
    fam = utils.short.general_fam_of(each)
    names.append(each)
    names_by_family[fam].append(each)
print(names_by_family)

no_bg_names = remove_bg(names)
no_bg_clusters = remove_bg_from_clusters(clusters)
no_bg_name_by_family = {
    fam: remove_bg(names)
    for fam, names in names_by_family.items()
    if len(remove_bg(names)) > 0
}

print('no_bg_name_by_family:', no_bg_name_by_family)


class EvaluateTest(unittest.TestCase):
    def test_remove_bg(self):
        no_bg = remove_bg(names)
        print(no_bg)
        self.assertListEqual(no_bg, ['RF01_A', 'RF01_B', 'RF02_C', 'RF02_D', 'RF01_E', 'RF01_F'])

    def test_remove_bg_from_clusters(self):
        no_bg = remove_bg_from_clusters(clusters)
        print(no_bg)
        self.assertListEqual(no_bg, [['RF01_A', 'RF01_B', 'RF02_C'], ['RF02_D'], ['RF01_E', 'RF01_F']])

    def test_is_dominated_by(self):
        fam, cnt = dominator_of(clusters[0])
        self.assertEqual(fam, 'RF01')
        self.assertEqual(cnt, 2)

    def test_sensitivity_of(self):
        res = sensitivity_of('RF01', no_bg_clusters, no_bg_name_by_family)
        self.assertAlmostEqual(res, 1.0)
        res = sensitivity_of('RF02', no_bg_clusters, no_bg_name_by_family)
        self.assertAlmostEqual(res, 0.5)

    def test_precision_of(self):
        res = precision_of('RF01', no_bg_clusters)
        self.assertAlmostEqual(res, 0.8)
        res = precision_of('RF02', no_bg_clusters)
        self.assertAlmostEqual(res, 1.0)
        res = precision_of('RF03', no_bg_clusters)
        self.assertAlmostEqual(res, 0)

    def test_family_cnt_in_cluster(self):
        res = family_cnt_in_cluster('RF01', clusters[0])
        self.assertEqual(res, 2)
        res = family_cnt_in_cluster('RF02', clusters[1])
        self.assertEqual(res, 1)

    def test_max_in_cluster(self):
        res = max_in_cluster_of('RF01', no_bg_clusters, names_by_family)
        self.assertAlmostEqual(res, 0.5)
        res = max_in_cluster_of('RF02', no_bg_clusters, names_by_family)
        self.assertAlmostEqual(res, 0.5)

    def test_nofold_get_name_clusters(self):
        from os.path import join
        path = join(utils.path.queries_path(), 'rfam75id',
                    'rfam75id.clusters_s3rSpec_top.txt_expanded_merged_bs17.41bgNoneGloc.txt')
        clusters = nofold_get_name_clusters(path)
        print(clusters)
        self.assertEqual(len(clusters), 20)

    def test_run(self):
        res, avg = run(names, clusters)
        self.assertListEqual(res.keys(), ['family', 'sensitivity', 'precision', 'max_in_cluster', 'seq_cnt'])
        print(res)
        self.assertListEqual(res['family'], ['RF01', 'RF02'])
        self.assertListEqual(res['sensitivity'], [
            1.0, 0.5
        ])
        self.assertListEqual(res['precision'], [
            0.8, 1.0
        ])
        self.assertListEqual(res['max_in_cluster'], [
            0.5, 0.5
        ])
        self.assertListEqual(res['seq_cnt'], [
            4, 2
        ])

        self.assertListEqual(avg.keys(), ['sensitivity', 'precision', 'max_in_cluster'])
        print(avg)
        self.assertAlmostEqual(avg['sensitivity'], (1.0 * 4 + 0.5 * 2) / 6)
        self.assertAlmostEqual(avg['precision'], (0.8 * 4 + 1.0 * 2) / 6)
        self.assertAlmostEqual(avg['max_in_cluster'], (0.5 * 4 + 0.5 * 2) / 6)

    def test_real(self):
        from os.path import join
        file = join(utils.path.results_path(), 'combined.novel-1-2-3hp.labelSpreading.refined.cluster')
        utils.run.run_python_attach_output(
            join(utils.path.src_path(), 'evaluate.py'),
            file=file,
            query='novel-1-2-3hp'
        )
        from os.path import exists
        self.assertTrue(exists(file + '.evaluation'))

    def test_real_large(self):
        from os.path import join
        file = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.refined.cluster')
        utils.run.run_python_attach_output(
            join(utils.path.src_path(), 'evaluate.py'),
            file=file,
            query='rfam75id-rename'
        )
        from os.path import exists
        self.assertTrue(exists(file + '.evaluation'))
