import unittest
from src import utils


class ShortTest(unittest.TestCase):
    def test_is_name(self):
        self.assertTrue(utils.short.is_name('QRF00001'))
        self.assertTrue(utils.short.is_name('RF00001'))
        self.assertFalse(utils.short.is_name('novel1-2-3hp'))

    def test_is_bg(self):

        self.assertTrue(utils.short.is_bg('dinucShuffaoeu'))
        self.assertTrue(utils.short.is_bg('bg1234'))
        self.assertTrue(utils.short.is_bg('bg_1234'))

        self.assertFalse(utils.short.is_bg('RF1234'))
        self.assertFalse(utils.short.is_bg('QRF1234123'))

    def test_fam_of(self):

        self.assertEqual(utils.short.fam_of('RF1234_abcde'), 'RF1234')
        self.assertRaises(ValueError, utils.short.fam_of, 'QRF1234_abc')

    def test_qfam_of(self):
        self.assertRaises(ValueError, utils.short.qfam_of, 'RF1234_abc')
        self.assertEqual(utils.short.qfam_of('QRF1234_abc'), 'RF1234')

    def test_general_fam_of(self):
        self.assertEqual(utils.short.general_fam_of('ABC_DEF'), 'ABC')

    def test_normalize_array(self):

        arr = [9, 10, 11]
        res = utils.short.normalize_array(arr)
        print(res)
        for each in res:
            self.assertTrue(-2 < each < 2, 'after z-normalization the range should be quite small')

    def test_identical_clusters(self):
        A = [
            [1, 2, 3],
            [4, 5]
        ]
        B = [
            [5, 4],
            [2, 3, 1]
        ]
        self.assertTrue(utils.short.identical_clusters(A, B))
        C = [
            [5, 4],
            [2, 3, 2]
        ]
        self.assertFalse(utils.short.identical_clusters(A, C))

    def test_list_equal(self):
        A = [1, 2, 3]
        B = [1, 2, 3, 4]

        self.assertFalse(utils.short.list_equal(A, B))

        C = [3, 2, 1]
        self.assertFalse(utils.short.list_equal(A, C))

        D = [1, 2, 3]
        self.assertTrue(utils.short.list_equal(A, D))

    def test_sliding_window(self):
        l = [1, 2, 3]
        r = list(utils.short.sliding_window(l, 2))
        print(r)
        self.assertListEqual(r, [(1, 2), (2, 3)])

    def test_zeros(self):
        for i, zero in zip(range(10), utils.short.zeros()):
            self.assertEqual(zero, 0)

    def test_weighted_random(self):
        total = 1000000
        possibles = ['a', 'b', 'c', 'd']
        prob = [0.1, 0.2, 0.3, 0.4]
        r = utils.short.weighted_random(total, possibles, prob)
        from collections import Counter
        cnt = Counter()
        for each in r:
            cnt[each] += 1
        for label, p in zip(possibles, prob):
            c = float(cnt[label]) / total
            self.assertAlmostEqual(c, p, 2)

    def test_unit_normalize(self):
        l = [1,2,3,4]
        ll = utils.short.unit_normalize(l)
        self.assertListEqual(ll, [0.1, 0.2, 0.3, 0.4])

    def test_datetime_now(self):
        r = utils.short.datetime_now()
        print(r)
