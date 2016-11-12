import unittest
from src.utils.helpers import sizeof

class SizeOfTest(unittest.TestCase):

    def test_size_easy(self):

        s = 'abc'
        c = 'a'
        i = 1
        f = 1.1

        self.assertEqual(sizeof.total_size(c), 38)
        self.assertEqual(sizeof.total_size(s), 38 + 2)

        self.assertEqual(sizeof.total_size(i), 24)
        self.assertEqual(sizeof.total_size(f), 24)


    def test_size_list(self):
        l = []
        self.assertEqual(sizeof.total_size(l), 72)

        ll = [1]
        self.assertEqual(sizeof.total_size(ll), 72 + 24 + 8)

    def test_size_complex(self):
        l = [[], [1]]

        import sys
        print(sizeof.total_size(l), sys.getsizeof(l))
        self.assertGreater(sizeof.total_size(l), sys.getsizeof(l))

