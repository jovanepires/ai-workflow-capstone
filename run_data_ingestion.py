import re
import os
import sys
import numpy as np
import pandas as  pd

from app.data_ingestion.data_utils import DataUtils
from app.data_ingestion.data_repository import DataRepository
from settings import DATA_DIR_TRAIN, LOAD_DATA

if __name__ == "__main__":
    data_dir = DATA_DIR_TRAIN

    if LOAD_DATA == 'y':
        if not data_dir:
            raise ValueError("Environment variable DATAPATH are not defined!")

        ## init repository
        data_repository = DataRepository()

        ## load invoices
        invoices_df = (DataUtils()).load_all_json_files(data_dir).convert_to_dataframe(output=True)
        data_repository.connect_db().insert_invoices(invoices_df)

        ## top 10 countries
        table = pd.pivot_table(invoices_df, index='country', values="price", aggfunc='sum')
        table.columns = ['total_revenue']
        table.sort_values(by='total_revenue', inplace=True, ascending=False)
        top_ten_countries =  np.array(list(table.index))[:10]
        data_repository.connect_db().insert_countries(pd.DataFrame({"name": top_ten_countries}))

        ## transform revenues
        dfs = {}
        dfs['all'] = (DataUtils()).convert_dataframe_to_ts(dataframe=invoices_df, output=True)
        dfs['all']['country_id'] = 'all'
        dfs['all']['country'] = 'all'

        for country in list(top_ten_countries):
            country_id = re.sub("\s+","_",country.lower())
            df_country = (DataUtils()).convert_dataframe_to_ts(dataframe=invoices_df, country=country, output=True)
            df_country['country_id'] = country_id
            df_country['country'] = country
            dfs[country_id] = df_country
        
        ## clean the table "revenues"
        data_repository.connect_db().drop_table("revenues")

        ## load revenues
        for key in list(dfs.keys()):
            data_repository.connect_db().insert_revenues(dfs[key])
