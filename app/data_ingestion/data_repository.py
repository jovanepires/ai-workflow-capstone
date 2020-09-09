import re
import os
import sys
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from app.logger import logger
from . import data_utils

logger.get_logger('general', __name__)

class DataRepository():
    def __init__(self):
        self._eng = create_engine("sqlite:///invoices.db")
        self._conn = None
        self._table = 'invoices'

    def connect_db(self):
        """
        function to connection to database
        """
        try:
            self._conn = self._eng.connect()
            logger.info(msg="...successfully connected to db")
        except Exception as e:
            logger.info(msg="...unsuccessful connection: {}".format(e))
        
        return self

    def insert(self, dataframe):
        try:
            with self._conn as conn:
                dataframe.to_sql(self._table, con=self._conn, if_exists='replace')
                logger.info(msg="...successfully inserted to db")
        except Exception as e:
            logger.info(msg="...unsuccessful insert: {}".format(e))

    def list(self, index_col='date'):
        """
        load and clean the db data
        """
        with self._conn as conn:
            return pd.read_sql_table(self._table, conn, index_col=index_col)

    def list_ts(self, index_col=None):
        """
        load and clean the db data
        """
        with self._conn as conn:
            ## get original data
            df = pd.read_sql_table(self._table, conn, index_col=index_col)

            ## find the top ten countries (wrt revenue)
            table = pd.pivot_table(df,index='country',values="price",aggfunc='sum')
            table.columns = ['total_revenue']
            table.sort_values(by='total_revenue',inplace=True,ascending=False)
            top_ten_countries =  np.array(list(table.index))[:10]

            # file_list = [os.path.join(data_dir,f) for f in os.listdir(data_dir) if re.search("\.json",f)]
            # countries = [os.path.join(data_dir,"ts-"+re.sub("\s+","_",c.lower()) + ".csv") for c in top_ten_countries]

            ## load the data
            dfs = {}
            dfs['all'] = (data_utils.DataUtils()).convert_dataframe_to_ts(dataframe=df, output=True)
            for country in top_ten_countries:
                country_id = re.sub("\s+","_",country.lower())
                dfs[country_id] = (data_utils.DataUtils()).convert_dataframe_to_ts(dataframe=df, country=country, output=True)
        
            return dfs
