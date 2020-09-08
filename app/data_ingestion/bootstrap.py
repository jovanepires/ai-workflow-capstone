import os

from app.data_ingestion.data_utils import DataUtils
from app.data_ingestion.data_repository import DataRepository

if __name__ == "__main__":
    data_dir = os.getenv("DATAPATH")

    if not data_dir:
        raise ValueError("Environment variable DATAPATH are not defined!")

    data_handler = DataUtils()
    data_repository = DataRepository()

    data_handler = DataUtils()
    invoices_df_ts = data_handler.load_all_json_files(data_dir)\
                          .convert_to_dataframe(output=False)\
                          .convert_dataframe_to_ts(index_column="date")

    data_repository.insert(invoices_df_ts)