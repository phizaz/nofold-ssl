import unittest

import utils
from os.path import normpath, join


class PathTest(unittest.TestCase):
    def test_utils_path(self):
        self.assertEqual(normpath(utils.path.utils_path()),
                         normpath('/Users/phizaz/Projects/nofold-ssl/src/utils'))

    def test_root_path(self):
        self.assertEqual(normpath(utils.path.root_path()),
                         normpath('/Users/phizaz/Projects/nofold-ssl/'))

    def test_src_path(self):
        self.assertEqual(normpath(utils.path.src_path()),
                         normpath('/Users/phizaz/Projects/nofold-ssl/src'))

    def test_queries_path(self):
        self.assertEqual(normpath(utils.path.queries_path()),
                         normpath('/Users/phizaz/Projects/nofold-ssl/queries'))

    def test_db_path(self):
        self.assertEqual(normpath(utils.path.db_path()),
                         normpath('/Users/phizaz/Projects/nofold-ssl/Rfam-seed/db'))

    def test_get_cm_paths(self):
        paths = utils.path.get_cm_paths()
        self.assertEqual(len(paths), 1973)

    def test_results_path(self):
        path = utils.path.results_path()
        self.assertEqual(normpath(path), normpath('/Users/phizaz/Projects/nofold-ssl/results'))

class MakePathTest(unittest.TestCase):

    test_path = join(utils.path.root_path(), '_test_', '_sub_test_')

    def rm_dir(self):
        import os
        from os.path import dirname
        try:
            os.rmdir(self.test_path)
            os.rmdir(dirname(self.test_path))
        except OSError as e:
            pass

    def setUp(self):
        self.rm_dir()

    def tearDown(self):
        self.rm_dir()

    def test_make_path(self):
        utils.path.make_path(self.test_path)

        from os.path import exists, dirname
        self.assertTrue(exists(self.test_path))
        self.assertTrue(exists(dirname(self.test_path)))