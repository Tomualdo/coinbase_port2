import json
import pandas as pd
import os
from datetime import datetime, timedelta
from pprintpp import pprint as pp
import natsort

ROOT_DIR = os.path.abspath(os.curdir)

older_json = 'dataOMG-EUR20201028.json'
newer_json = 'dataOMG-EUR20201104.json'


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
    # load each dataFrame file and store in list
    for data_file in data_files:
        with open(product_folder+'/'+data_file) as act_file:

            fil = json.load(act_file)
            for idx in range(len(fil[current_product])):
                mer[current_product].append(fil[current_product][idx])
           
    return mer


a = load_candle_data_days('OMG-EUR',3)

print(a['OMG-EUR'][0])
print(a['OMG-EUR'][-1])

# with open('test_MERGED_days.json','w') as df: 
#         json.dump(a, df, indent=4)