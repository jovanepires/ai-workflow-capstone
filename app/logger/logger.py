import time
import os
import re
import csv
import sys
import uuid
import joblib
import numpy as np

from datetime import date


class Logger():

    def __init__(self):
        today = date.today()
        ## name the logfile using something that cycles with date (day, month, year)    
        self._file = "{}-{}-{}-{}.log".format('general', __name__, today.year, today.month)
        self._logger = os.path.abspath(os.path.join('logs', self._file))

    def get_logger(self, country, method, verbose=True):
        today = date.today()
        ## name the logfile using something that cycles with date (day, month, year)   
        self._verbose = verbose 
        self._file = "{}-{}-{}-{}.log".format(country, method, today.year, today.month)
        self._logger = os.path.abspath(os.path.join('logs', self._file))
        return self

    def info(self, **kwargs):
        """
        update log file

        for predict/train
            -> y_pred, y_proba, query, runtime, model_version

        for general info
            -> msg
        """

        ## write the data to a csv file    
        header = ['unique_id','timestamp', *kwargs.keys()]
        write_header = False
        if not os.path.exists(self._logger):
            write_header = True
        with open(self._logger,'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            if write_header:
                writer.writerow(header)

            line = [kwargs.get(k, None) for k in header]
            line[0] = uuid.uuid4()
            line[1] = time.time()

            to_write = list(map(str, line))
            writer.writerow(to_write)

            if self._verbose:
                print(','.join(to_write))