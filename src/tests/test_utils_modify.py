import unittest
from src import utils


class ModifyTest(unittest.TestCase):
    def test_retain_bitscore_cols(self):
        header = ['a', 'b', 'c']
        points = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        _points, _header = utils.modify.retain_bitscore_cols(['a', 'c'], points, header)
        self.assertListEqual(_points, [[1, 3], [4, 6], [7, 9]])
        self.assertListEqual(_header, ['a', 'c'])
