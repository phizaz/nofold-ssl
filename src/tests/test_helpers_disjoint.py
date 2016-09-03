import unittest
from src import utils
from src.utils.helpers import disjoint

class DisjointTest(unittest.TestCase):

    def test(self):
        s = disjoint.DisjointSet(10)
        s.join(0, 1)
        self.assertTrue(s.common(0, 1))
        s.join(2, 3)
        s.join(0, 2)
        self.assertTrue(s.common(1, 3))
        self.assertEqual(s.parent(0), s.parent(2))
        self.assertFalse(s.common(0, 9))