import re
import os
import sys
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.logger import logger
from . import data_utils

logger.get_logger("general", __name__)

class DataRepository():
    def __init__(self):
        self._eng = create_engine("sqlite:///invoices.db")
        self._conn = None
        self._invoices_table = "invoices"
        self._revenues_table = "revenues"
        self._countries_table = "countries"
        self._predictions_table = "predictions"


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


    def insert(self, dataframe, table, if_exists="replace"):
        try:
            with self._conn as conn:
                dataframe.to_sql(table, con=self._conn, if_exists=if_exists)
                logger.info(msg="...successfully inserted to db")
        except Exception as e:
            logger.info(msg="...unsuccessful insert: {}".format(e))


    def insert_invoices(self, dataframe, if_exists="replace"):
        self.insert(dataframe=dataframe, table=self._invoices_table, if_exists=if_exists)
    

    def insert_revenues(self, dataframe, if_exists="append"):
        self.insert(dataframe=dataframe, table=self._revenues_table, if_exists=if_exists)
    

    def insert_countries(self, dataframe, if_exists="replace"):
        self.insert(dataframe=dataframe, table=self._countries_table, if_exists=if_exists)


    def insert_predictions(self, dataframe, if_exists="append"):
        self.insert(dataframe=dataframe, table=self._predictions_table, if_exists=if_exists)


    def list_invoices(self, index_col=None):
        """
        list invoices
        """
        with self._conn as conn:
            return pd.read_sql_table(self._invoices_table, conn, index_col=index_col)


    def list_revenues(self, country="all", index_col=None):
        """
        list revenues
        """
        with self._conn as conn:
            query = "SELECT * FROM %s WHERE country_id = ?" % self._revenues_table
            param = [country]
            dates = ["date"]
            df = pd.read_sql_query(sql=query,
                                   con=conn,
                                   index_col=index_col,
                                   params=param,
                                   parse_dates=dates)

            return df


    def list_predictions(self, country="all", index_col=None):
        """
        list predictions
        """
        with self._conn as conn:
            query = "SELECT * FROM %s WHERE country_id = ?" % self._predictions_table
            param = [country]
            dates = ["date"]
            df = pd.read_sql_query(sql=query,
                                   con=conn,
                                   index_col=index_col,
                                   params=param,
                                   parse_dates=dates)

            return df


    def list_countries(self, index_col=None):
        """
        list countries 
        """
        with self._conn as conn:
            return pd.read_sql_table(self._countries_table, conn, index_col=index_col)


    def drop_table(self, table_name):
        with self._conn as conn:
            base = declarative_base()
            metadata = MetaData(conn, reflect=True)
            table = metadata.tables.get(table_name)
            if table is not None:
                logger.info(msg="...deleting table: {}".format(table))
                base.metadata.drop_all(conn, [table], checkfirst=True)
