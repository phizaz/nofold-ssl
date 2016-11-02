import unittest
import logging

class LoggingTest(unittest.TestCase):

    def test_logging(self):
        logger = logging.getLogger('a')
        logger.setLevel(logging.INFO)
        logger.info('aoeu')