import unittest
import itertools

class CountTest(unittest.TestCase):

    def test_count(self):

        count = itertools.count(1)
        print(count)

        self.assertEqual(count.next(), 1)
        self.assertEqual(count.next(), 2)