import os
import json
import sys
import re
import shutil
import time
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import defaultdict
from datetime import datetime
from pandas.plotting import register_matplotlib_converters

from app.logger import logger

register_matplotlib_converters()

class DataUtils():
    def __init__(self):
        self._items_dict = []
        self._invoices_df = pd.DataFrame()
        self._invoices_df_ts = pd.DataFrame()

    def clear_column_name(self, col, fix):
        tmp = col.lower().replace('_', '').replace('-', '').strip()
        new = fix.get(tmp, col)
        return col, new

    def load_all_json_files(self, data_path, output=False):
        """
        laod all json formatted files into a dict
        """
        items_files = os.listdir(data_path)
        rename_columns = {'totalprice': 'price', 'streamid': 'stream_id', 'timesviewed': 'times_viewed'}

        for invoice_file in items_files:
            with open(os.path.join(data_path, invoice_file)) as f:
                logger.info(msg=("loading {}".format(invoice_file)))
                documents = json.load(f)
                for d in documents:
                    for k in list(d.keys()):
                        col, new = self.clear_column_name(k, rename_columns)
                        d[new] = d.pop(new, None)
                        d[new] = d.pop(col, None)
                        
                self._items_dict = [*self._items_dict, *documents]

        logger.info(msg=("{} items loaded".format(len(self._items_dict))))

        if output:
            return self._items_dict

        return self

    def convert_to_dataframe(self, data_object=None, date_column=None, output=True):
        """
        convert loaded dict to dataframe
        """
        data = data_object if data_object else self._items_dict
        dt_columns = date_column if date_column else ['year', 'month', 'day']
        self._invoices_df = pd.DataFrame.from_dict(data) 
        self._invoices_df['invoice_date'] = pd.to_datetime(self._invoices_df[dt_columns].apply(
                                            lambda row: '-'.join(row.values.astype(str)), axis=1))
    
        ## sort by date and reset the index
        self._invoices_df.sort_values(by='invoice_date', inplace=True)
        self._invoices_df.reset_index(drop=True, inplace=True)

        logger.info(msg=("{} items converted to time series".format(len(self._invoices_df))))

        if output:
            return self._invoices_df

        return self

    def convert_dataframe_to_ts(self, index_column=None, dataframe=None, value_column=None, resample=None, country=None, output=True):
        """
        given the original DataFrame 
        return a numerically indexed time-series DataFrame 
        by aggregating over each day
        """
        data = self._invoices_df
        
        if isinstance(dataframe, pd.DataFrame):
            data = dataframe

        if country:
            if country not in np.unique(data['country'].values):
                raise Excpetion("country not found")
        
            mask = data['country'] == country
            df = data[mask]
        else:
            df = data
            
        ## use a date range to ensure all days are accounted for in the data
        invoice_dates = df['invoice_date'].values
        start_month = '{}-{}'.format(df['year'].values[0], str(df['month'].values[0]).zfill(2))
        stop_month = '{}-{}'.format(df['year'].values[-1], str(df['month'].values[-1]).zfill(2))
        df_dates = df['invoice_date'].values.astype('datetime64[D]')
        days = np.arange(start_month,stop_month, dtype='datetime64[D]')
        
        purchases = np.array([np.where(df_dates==day)[0].size for day in days])
        invoices = [np.unique(df[df_dates==day]['invoice'].values).size for day in days]
        streams = [np.unique(df[df_dates==day]['stream_id'].values).size for day in days]
        views =  [df[df_dates==day]['times_viewed'].values.sum() for day in days]
        revenue = [df[df_dates==day]['price'].values.sum() for day in days]
        year_month = ["-".join(re.split("-",str(day))[:2]) for day in days]

        df_time = pd.DataFrame({'date':days,
                                'purchases':purchases,
                                'unique_invoices':invoices,
                                'unique_streams':streams,
                                'total_views':views,
                                'year_month':year_month,
                                'revenue':revenue})

        self._invoices_df_ts = df_time

        if output:
            return self._invoices_df_ts

        return self


    def make_features_to_ts(self, dataframe=None, training=True):
        """
        for any given day the target becomes the sum of the next days revenue
        for that day we engineer several features that help predict the summed revenue
        
        the 'training' flag will trim data that should not be used for training
        when set to false all data will be returned
        """

        if isinstance(dataframe, pd.DataFrame):
            self._invoices_df_ts = dataframe 

        ## extract dates
        dates = self._invoices_df_ts['date'].values.copy()
        dates = dates.astype('datetime64[D]')

        ## engineer some features
        eng_features = defaultdict(list)
        previous =[7, 14, 28, 70]  #[7, 14, 21, 28, 35, 42, 49, 56, 63, 70]
        y = np.zeros(dates.size)
        for d,day in enumerate(dates):

            ## use windows in time back from a specific date
            for num in previous:
                current = np.datetime64(day, 'D') 
                prev = current - np.timedelta64(num, 'D')
                mask = np.in1d(dates, np.arange(prev,current,dtype='datetime64[D]'))
                eng_features["previous_{}".format(num)].append(self._invoices_df_ts[mask]['revenue'].sum())

            ## get get the target revenue    
            plus_30 = current + np.timedelta64(30,'D')
            mask = np.in1d(dates, np.arange(current,plus_30,dtype='datetime64[D]'))
            y[d] = self._invoices_df_ts[mask]['revenue'].sum()

            ## attempt to capture monthly trend with previous years data (if present)
            start_date = current - np.timedelta64(365,'D')
            stop_date = plus_30 - np.timedelta64(365,'D')
            mask = np.in1d(dates, np.arange(start_date,stop_date,dtype='datetime64[D]'))
            eng_features['previous_year'].append(self._invoices_df_ts[mask]['revenue'].sum())

            ## add some non-revenue features
            minus_30 = current - np.timedelta64(30,'D')
            mask = np.in1d(dates, np.arange(minus_30,current,dtype='datetime64[D]'))
            eng_features['recent_invoices'].append(self._invoices_df_ts[mask]['unique_invoices'].mean())
            eng_features['recent_views'].append(self._invoices_df_ts[mask]['total_views'].mean())

        X = pd.DataFrame(eng_features)
        ## combine features in to df and remove rows with all zeros
        X.fillna(0,inplace=True)
        mask = X.sum(axis=1)>0
        X = X[mask]
        y = y[mask]
        dates = dates[mask]
        X.reset_index(drop=True, inplace=True)

        if training == True:
            ## remove the last 30 days (because the target is not reliable)
            mask = np.arange(X.shape[0]) < np.arange(X.shape[0])[-30]
            X = X[mask]
            y = y[mask]
            dates = dates[mask]
            X.reset_index(drop=True, inplace=True)
        
        return(X,y,dates)
