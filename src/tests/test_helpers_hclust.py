import unittest
import utils
import utils.helpers.hclust as hclust

class HClustTest(unittest.TestCase):

    def test(self):
        clust = hclust.HierarchicalClustMaxMergeDist()

        points = [
            [1,1], [0, 0], [3,3], [4,4]
        ]

        res = clust.fit(points, 1.5, method='average')
        self.assertEqual(len(res), 4)
        self.assertEqual(res[0], res[1])
        self.assertEqual(res[2], res[3])
        self.assertNotEqual(res[0], res[2])
