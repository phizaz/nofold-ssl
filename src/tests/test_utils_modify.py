import unittest
from src import utils


class ModifyTest(unittest.TestCase):
    def test_retain_bitscore_cols(self):
        header = ['a', 'b', 'c']
        points = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        _points, _header = utils.modify.retain_bitscore_cols(['a', 'c'], points, header)
        self.assertListEqual(_points, [[1, 3], [4, 6], [7, 9]])
        self.assertListEqual(_header, ['a', 'c'])

    def test_group_bitscore_by_family(self):
        names = ['A_1', 'A_2', 'B_1']
        points = [1, 2, 3]
        groups = utils.modify.group_bitscore_by_family(names, points)
        print(groups)
        self.assertDictEqual(groups, dict(A=[1,2], B=[3]))

    def test_group_names_by_family(self):
        names = [
            'RF0001_A',
            'RF0001_B',
            'RF0002_C',
            'QRF0002_D',
            'BG0001'
        ]

        group = utils.modify.group_names_by_family(names)
        print(group)
        self.assertListEqual(group['RF0002'], ['RF0002_C', 'QRF0002_D'])
        self.assertListEqual(group['RF0001'], ['RF0001_A', 'RF0001_B'])
        cnt = sum(len(each) for each in group.values())
        self.assertEqual(cnt, 4, 'BG should not appear in the group')