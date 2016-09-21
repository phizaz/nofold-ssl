import unittest
from src.utils.helpers import lmethod
from src import utils
from os.path import join

class LMethodTest(unittest.TestCase):

    def test_cluster_cnt(self):
        data = [
            [1,0,0,0,0],
            [0,1,0,0,0],
            [0,0,1,0,0],
            [0,0,0,1,0],
            [0,0,0,0,1],
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
            # [0.9, 0.1, 0, 0, 0],
            # [0.1, 0.9, 0, 0, 0],
        ]

        cnt = lmethod.get_clusters_cnt(data)
        print(cnt)
        self.assertEqual(cnt, 5)