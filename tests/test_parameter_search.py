import unittest
from src.parameter_search import *
from src import utils


class ParameterSearchTest(unittest.TestCase):
    def test_avg_cripple_itr(self):
        cnt = 0
        for _ in avg_cripple_itr(0):
            cnt += 1
        self.assertEqual(cnt, 1)

        cnt = 0
        for _ in avg_cripple_itr(10):
            cnt += 1
        self.assertEqual(cnt, 10)

    def test_avg_results(self):
        def d(sense, prec, max_in):
            return {'sensitivity': sense, 'precision': prec, 'max_in_cluster': max_in}

        raw = {
            'a': [
                d(1, 1, 1),
                d(0, 0, 0)
            ],
            'b': [
                d(0.2, 0.2, 0.2)
            ]
        }
        results = avg_results(raw)
        self.assertDictEqual(results, {'a': {'max_in_cluster': 0.5, 'sensitivity': 0.5, 'precision': 0.5},
                                       'b': {'max_in_cluster': 0.2, 'sensitivity': 0.2, 'precision': 0.2}}
                             )

    def test_run_combine(self):
        query = 'rfam75id-rename'
        cripple = 0
        nn_seed = 3
        names, points, header = run_combine(query, False, cripple, nn_seed, True)
        print(len(names))
        print(len(points))
        print(len(header))
        self.assertEqual(len(names), len(points))
        self.assertEqual(len(names), 4879)
        self.assertEqual(len(header), 1929)

    def test_run_normalized(self):
        from os.path import join
        path = join(utils.path.tests_supplies_path(), 'results', 'combined.rfam75id-rename.cripple0.bitscore')
        names, points, header = utils.get.get_bitscores(path)

        def almost_equal(a, b):
            return abs(a - b) < 1e-3

        self.assertTrue(almost_equal(1, 1.0001))
        self.assertFalse(almost_equal(1, 1.1))

        def list_not_equal(l1, l2):
            return any(not almost_equal(a, b) for a, b in zip(l1, l2))

        self.assertTrue(list_not_equal([1, 2, 3], [1, 2, 4]))
        self.assertFalse(list_not_equal([1, 2, 3], [1, 2, 3]))
        self.assertFalse(list_not_equal([1.0001, 2.0001], [0.9999, 1.99999]))

        query = 'rfam75id-rename'
        l_names, l_points, l_header = run_normalize(names, points, header, query, True)
        nl_names, nl_points, nl_header = run_normalize(names, points, header, query, False)

        self.assertListEqual(l_names, nl_names)

        self.assertEqual(len(l_points), len(nl_points))
        for a, aa in zip(l_points, l_points):
            self.assertFalse(list_not_equal(a, aa))
        for l_point, nl_point in zip(l_points, nl_points):
            self.assertTrue(list_not_equal(l_point, nl_point),
                            msg='normalization has no effect ! {} = {}'.format(l_point, nl_point))

        self.assertListEqual(l_header, nl_header)

        print(l_points[0])
        print(nl_points[0])

    def test_run_clustering(self):
        from os.path import join
        path = join(utils.path.tests_supplies_path(), 'results',
                    'combined.rfam75id-rename.cripple0.normalized.bitscore')
        names, points, header = utils.get.get_bitscores(path)
        clusters = run_clustering(names, points, header, 'labelSpreading', 'rbf', 0.5, 1.0, True)
        from src.utils.helpers import space
        for cluster in clusters:
            self.assertIsInstance(cluster, space.Cluster)
        print(len(clusters))

    def test_run_cluster_refinement(self):
        from os.path import join
        point_file = join(utils.path.tests_supplies_path(), 'results',
                          'combined.rfam75id-rename.cripple0.normalized.bitscore')
        names, points, header = utils.get.get_bitscores(point_file)

        path = join(utils.path.results_path(), 'combined.rfam75id-rename.cripple0.labelSpreading.cluster')
        clusters = utils.get.get_clusters(path, point_file)

        clusters = run_cluster_refinement(clusters, names, points, header, 1.0, True)
        print(len(clusters))

    def test_run_evaluate(self):
        from os.path import join
        path = join(utils.path.tests_supplies_path(), 'results',
                    'combined.rfam75id-rename.cripple0.labelSpreading.refined.cluster')
        clusters = utils.get.get_name_clusters(path)
        names = [
            rec.name
            for rec in utils.get.get_query_records('rfam75id-rename')
            if not utils.short.is_bg(rec.name)
            ]

        average = run_evaluate(clusters, names)
        print(average)

        self.assertAlmostEqual(average['sensitivity'], 1.0)
        self.assertAlmostEqual(average['precision'], 1.0)
        self.assertGreater(average['max_in_cluster'], 0.8)

    def test_get_all_arguments(self):
        args = get_all_arguments()
        self.assertListEqual(args,
                             ['query', 'unformatted', 'cripple', 'nn_seed', 'inc_centroids', 'components',
                              'length_norm',
                              'alg', 'kernel', 'gamma', 'alpha', 'multilabel', 'c', 'merge']
                             )

    def test_save(self):
        args = ['a', 'b', 'c']
        results = {
            (1, 2, 3): {
                'sensitivity': 4,
                'precision': 5,
                'max_in_cluster': 6
            }
        }
        cols, rows = save(args, results)
        self.assertListEqual(cols, ['a', 'b', 'c', 'sensitivity', 'precision', 'max_in_cluster'])
        self.assertListEqual(rows, [(1, 2, 3, 4, 5, 6)])

    def test_load_search_space_file(self):
        from os.path import join
        file = join(utils.path.tests_supplies_path(), 'search_space.json')
        search_space = load_search_space_file(file)
        print(search_space)
        self.assertDictEqual(search_space, {u'kernel': [u'rbf'], u'c': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                                            u'inc_centroids': [True, False],
                                            u'alg': [u'labelSpreading', u'labelPropagation'],
                                            u'cripple': [0, 0, 1, 6, 6], u'length_norm': [True, False],
                                            u'alpha': [0.6, 0.7, 0.8, 0.9, 1.0],
                                            u'unformatted': [False, False, False, False, False],
                                            u'query': [u'rfam75id-rename', u'rfam75id_embed-rename',
                                                       u'rfam75id_dinuc3000-rename',
                                                       u'fam40_typedistributed_embed+bg_weak',
                                                       u'fam40_typedistributed_plain+bg_weak'], u'gamma': [0.5],
                                            u'nn_seed': [1, 7, 13, 19]})


class ParameterLevelSearchTest(unittest.TestCase):
    query = [{
        'query': 'novel-1-2-3hp',
        'unformatted': True,
        'cripple': 0
    }]
    nn_seed = [1]
    inc_centroids = [False]
    components = [100]
    length_norm = [False]
    alg = ['labelSpreading']
    kernel = ['rbf']
    gamma = [0.5]
    alpha = [1.0]
    multilabel = [False]
    c = [1.2]
    merge = [False]

    search_space = {
        'query': query,
        'nn_seed': nn_seed,
        'inc_centroids': inc_centroids,
        'components': components,
        'length_norm': length_norm,
        'alg': alg,
        'kernel': kernel,
        'gamma': gamma,
        'alpha': alpha,
        'multilabel': multilabel,
        'c': c,
        'merge': merge
    }

    def test_get_job_cnt(self):
        search_space = self.search_space.copy()
        search_space['query'] = [
            {
                "unformatted": False,
                "query": "rfam75id-rename",
                "cripple": 0
            },
            {
                "unformatted": False,
                "query": "rfam75id-rename",
                "cripple": 1
            },
            {
                "unformatted": False,
                "query": "rfam75id-rename",
                "cripple": 2
            }
        ]
        self.assertEqual(get_job_cnt(search_space), 21)

    def test_search(self):
        results = param_search(self.search_space)
        print(results)
        idx = ('novel-1-2-3hp', True, 0, 1, False, 100, False, 'labelSpreading', 'rbf', 0.5, 1.0, False, 1.2, False)
        self.assertListEqual(results.keys(), [idx])
        row = results[idx]
        self.assertAlmostEqual(row['sensitivity'], 0.33333333333333331)
        self.assertAlmostEqual(row['precision'], 0.11111111111111109)
        self.assertAlmostEqual(row['max_in_cluster'], 1.0)
