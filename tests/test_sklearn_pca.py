from sklearn.decomposition import PCA
import unittest


class SklearnPCATest(unittest.TestCase):

    def test(self):

        arr = [
            [1,2,3],
            [4,5,6]
        ]
        pca = PCA(2)
        output = pca.fit_transform(arr)

        self.assertEqual(len(output[0]), 2)
