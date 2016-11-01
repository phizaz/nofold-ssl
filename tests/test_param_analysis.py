import unittest
from src.param_analysis import *
from src import utils
from os.path import join

class ParamAnalysisTest(unittest.TestCase):

    def test_open_result(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        print(rows)

    def test_row_score(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        score = row_score(rows[0])
        print(score)

    def test_sum_score_filter(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        s = sum_score_filter(get_filter('c', 1.2), rows)
        print(s)

    def test_many_filters(self):
        file = join(utils.path.results_path(),
                    'parameter_search.2016-09-03 14:13:10.465030-fam40-embed.csv')
        rows = open_result(file)
        f_rows = many_filters(['nn_seed', 'alg'], [13, 'labelSpreading'], rows)
        print(len(rows), len(f_rows))


    def test_main(self):
        main()

    def test_mean(self):
        a = mean([1,2,3])
        self.assertEqual(a, 2)

    def test_sd(self):
        a = sd([1,2,3])
        print(a)
