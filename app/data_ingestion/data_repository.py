import pandas as pd

from sqlalchemy import create_engine
from app.logger import logger

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