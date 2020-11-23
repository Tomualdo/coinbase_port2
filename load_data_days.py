import json
import pandas as pd
import os
from datetime import datetime, timedelta

ROOT_DIR = os.path.abspath(os.curdir)

def load_data_days(current_product):
    product_folder = ROOT_DIR+'/'+current_product
    # get files of data files in product folder
    data_files = [name for name in os.listdir(product_folder) if name.startswith("data")]
    pd_list = []
    # load each dataFrame file and store in list
    for data_file in data_files:
        with open(product_folder+'/'+data_file) as act_file:
            df = json.load(act_file)
            df = pd.json_normalize(df,current_product)
            pd_list.append(df)
    # concatinate all files to single data frame
    new_df = pd.concat(pd_list, ignore_index=True, verify_integrity=True)
    return new_df

