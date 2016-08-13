import unittest
from src import utils
class ShortTest(unittest.TestCase):

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
