import json
import pandas as pd
import os
from datetime import datetime, timedelta

ROOT_DIR = os.path.abspath(os.curdir)

current_product = 'XLM-EUR'
product_folder = ROOT_DIR+'/'+current_product
today_date = datetime.now().strftime("%Y%m%d")

# get files of data files in product folder
data_files = [name for name in os.listdir(product_folder) if name.startswith("data")]
print(data_files)

pd_list = []
for data_file in data_files:
    with open(product_folder+'/'+data_file) as act_file:
        df = json.load(act_file)
        df = pd.json_normalize(df,current_product)
        pd_list.append(df)
df = pd.concat(pd_list, ignore_index=True, verify_integrity=True)
# return new_df

print(df)

# print("THE LATEST record loaded {}".format(product_minute_candlestick[current_product][0]['time']))
# print("THE MOST RECENT record loaded {}".format(product_minute_candlestick[current_product][-1]['time']))

# df = pd.json_normalize(product_minute_candlestick,current_product)
#format the collumns
df = df.filter(items=['time','open','close','low'])
# print(df)

df[['open','close','low']] = df[['open','close','low']].apply(pd.to_numeric)
df[['time']] = pd.to_datetime(df['time'],format='%d.%m.%Y %H:%M')
df = df.set_index('time')

print(df)