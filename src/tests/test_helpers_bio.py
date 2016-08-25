import unittest
import utils
from utils.helpers import bio


class BioTest(unittest.TestCase):

    def test_expand(self):
        r = bio.expand('A')
        self.assertSetEqual(r, {'A'})
        r = bio.expand('N')
        self.assertSetEqual(r, {'A', 'C', 'G', 'T'})

    def test_expand_tuple(self):
        r = bio.expand_tuple(('A', 'C'))
        self.assertListEqual(r, ['AC'])
        r = bio.expand_tuple(('R', 'Y'))
        self.assertListEqual(r, ['AC', 'AT', 'GC', 'GT'])

    def test_dinuc_freq(self):
        seq = 'ACGT'
        r = bio.dinuc_freq(seq)
        self.assertEqual(r['AC'], 1)
        self.assertEqual(r['CG'], 1)
        self.assertEqual(r['GT'], 1)

        seq = 'ARRT'
        r = bio.dinuc_freq(seq)
        self.assertEqual(r['AA'], 2)
        self.assertEqual(r['AG'], 2)
        self.assertEqual(r['GA'], 1)
        self.assertEqual(r['GG'], 1)
        self.assertEqual(r['AT'], 1)
        self.assertEqual(r['GT'], 1)

    def test_transition_freq(self):
        seq = 'ACGT'
        r = bio.transition_freq(seq)
        self.assertEqual(r['AC']['CG'], 1)
        self.assertEqual(r['CG']['GT'], 1)

        seq = 'ART'
        r = bio.transition_freq(seq)
        self.assertEqual(r['AA']['AT'], 1)
        self.assertEqual(r['AG']['GT'], 1)

    def test_generate_background_each(self):
        raise NotImplementedError

    def test_get_length_distribution(self):
        raise NotImplementedError

    def test_generate_background(self):
        raise NotImplementedError

    def test_embed_sequence(self):
        raise NotImplementedError

    def test_embed(self):
        raise NotImplementedError

