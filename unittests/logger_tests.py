from datetime import date
import os
import sys
import csv
import unittest
from ast import literal_eval
import pandas as pd
from app.logger import logger

class LoggerTest(unittest.TestCase):
    """
    test the essential functionality
    """
        
    def test_01(self):
        """
        ensure log file is created
        """
        logger.get_logger("unittests", __name__, verbose=False)
        logger.info(msg="It's Alive")
        log_file = logger._logger

        self.assertTrue(os.path.exists(log_file))


    def test_02(self):
        """
        ensure that content can be retrieved from log file
        """
        logger.get_logger("unittests", __name__, verbose=False)
        log_file = logger._logger
        data = "It's Alive"
        logger.info(msg=data)

        df = pd.read_csv(log_file)
        logged_data = [i for i in df["msg"].copy()][-1]
        self.assertEqual(data, logged_data)


### Run the tests
if __name__ == '__main__':
    unittest.main()