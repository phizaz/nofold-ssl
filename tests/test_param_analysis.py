import unittest
from src.param_analysis import *
from src import utils
from os.path import join


class ParamAnalysisTest(unittest.TestCase):
    def test_dist_l1(self):
        import numpy as np
        a = np.array([0.1, 0.8, 0.8])
        res = dist_l1(a)
        self.assertAlmostEqual(res, 1.7)

    def test_dist_l2(self):
        import numpy as np
        a = np.array([0.1, 0.8, 0.0])
        b = np.array([0.3, 0.3, 0.3])
        self.assertLess(dist_l2(b), dist_l2(a))
        c = np.array([0.2, 0.2, 0.2])
        self.assertAlmostEqual(dist_l2(c), 0.346410161514)

    def test_errors_of(self):
        a = [0.9, 0.8, 0.5]
        err = errors_of(a)
        self.assertAlmostEqual(err[0], 0.1)
        self.assertAlmostEqual(err[1], 0.2)
        self.assertAlmostEqual(err[2], 0.5)

    def test_open_result(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        print(rows)

    def test_row_score(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        score = row_error(rows[0])
        print(score)

    def test_many_filters(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        f_rows = get_rows_filtered(['nn_seed', 'alg'], [13, 'labelSpreading'], rows)
        print(len(rows), len(f_rows))

    def test_mean(self):
        a = mean([1, 2, 3])
        self.assertEqual(a, 2)

    def test_sd(self):
        a = sd([1, 2, 3])
        print(a)
