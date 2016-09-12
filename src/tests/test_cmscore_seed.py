import unittest
from src import utils
from src import cmscore_seed
import os
os.environ['PATH'] += ':/usr/local/bin'

class CmscoreSeedTest(unittest.TestCase):

    def test_int_fam(self):
        all_fam = utils.get.get_all_families()
        int_fam = map(cmscore_seed.int_fam, all_fam)
        self.assertListEqual(int_fam[:3], [1,2,3])

    def test_run(self):
        r = cmscore_seed.run(None, None)
        print(r)