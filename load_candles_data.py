import json
import pandas as pd
import os
from datetime import datetime, timedelta
from pprintpp import pprint as pp
import natsort


ROOT_DIR = os.path.abspath(os.curdir)

older_json = 'dataOMG-EUR20201028.json'
newer_json = 'dataOMG-EUR20201104.json'

# def json_data_merge(older_json,newer_json,current_product):
#     """concatenate two json files of same product."""

#     product_folder = ROOT_DIR+'/'+current_product

#     with open(product_folder+'/'+older_json) as f:
#         old = json.load(f)
#     with open(product_folder+'/'+newer_json) as f:
#         new = json.load(f)

#     mer = {}
#     if current_product not in mer:
#         mer[current_product] =[]

#     for idx in range(len(new[current_product])):
#         old[current_product].append(new[current_product][idx])
#     return old

def load_candle_data_days(current_product,num_of_days=2):
    product_folder = ROOT_DIR+'/'+current_product
    # get files of data files in product folder
    data_files = [name for name in os.listdir(product_folder) if name.startswith("data")]
    pd_list = []

    mer = {}
    if current_product not in mer:
        mer[current_product] =[]
    data_files = data_files = natsort.natsorted(data_files,reverse=False)
    data_files = data_files[-num_of_days:]
    # print(data_files)
    
    # load each dataFrame file and store in list
    for data_file in data_files:
        with open(product_folder+'/'+data_file) as act_file:

            fil = json.load(act_file)
            if fil == {}:
                print("EMPTY data FILE !!!")
                break
            for idx in range(len(fil[current_product])):
                mer[current_product].append(fil[current_product][idx])
            
    return mer


# a = load_candle_data_days('OMG-EUR',3)

# print(a['OMG-EUR'][0])
# print(a['OMG-EUR'][-1])

# with open('test_MERGED_days.json','w') as df: 
#         json.dump(a, df, indent=4)
