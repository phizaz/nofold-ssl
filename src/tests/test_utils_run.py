import unittest
from src import utils


class RunTest(unittest.TestCase):
    def test_run_command(self):
        import sys
        from os.path import join
        output = utils.run.run_command(
            [sys.executable, join(utils.path.src_path(), 'tests', 'supplies', 'echo.py'), 'test'])
        self.assertEqual(output, 'test\n')

    def test_run_command_with_err(self):
        import sys
        from os.path import join

        from subprocess import CalledProcessError

        self.assertRaises(CalledProcessError, utils.run.run_command,
                          [sys.executable, join(utils.path.src_path(), 'tests', 'supplies', 'error.py')]
                          )

    def test_run_command_attach_output(self):
        utils.run.run_command_attach_output(['echo', 'test'])

    def test_run_command_attach_with_err(self):
        import sys
        from os.path import join

        from subprocess import CalledProcessError

        self.assertRaises(Exception, utils.run.run_command_attach_output,
                          [sys.executable, join(utils.path.src_path(), 'tests', 'supplies', 'error.py')]
                          )

    def test_run_python(self):
        from os.path import join

        output = utils.run.run_python(join(utils.path.src_path(), 'tests', 'supplies', 'echo.py'), 'test')
        self.assertEqual(output, 'test\n')

    def test_run_python_with_params(self):
        from os.path import join

        output = utils.run.run_python(join(utils.path.src_path(), 'tests', 'supplies', 'params.py'), 1, b=2, c=3)
        self.assertEqual(output, '1 2 3\n')

    def test_run_python_attach_output(self):
        from os.path import join

        utils.run.run_python_attach_output(join(utils.path.src_path(), 'tests', 'supplies', 'echo.py'), 'test')
