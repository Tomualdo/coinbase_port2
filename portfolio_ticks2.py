from numpy.core.multiarray import busday_count
import pandas as pd
import numpy as np
import websocket, json
import dateutil.parser
import json, hmac, hashlib, time, requests, base64
from pprintpp import pprint as pp
from datetime import datetime, timedelta 
import os
from portfolio2 import *

ROOT_DIR = os.path.abspath(os.curdir)

def json_data_merge(older_json,newer_json,current_product):
    """concatenate two json files of same product."""
    with open(older_json) as f:
        old = json.load(f)
    with open(newer_json) as f:
        new = json.load(f)

    mer = {}
    if current_product not in mer:
        mer[current_product] =[]

    for idx in range(len(new[current_product])):
        old[current_product].append(new[current_product][idx])
    return old

strategy_data = {
            "strategy_lower_bolling_lvl" : 2.6,
            "strategy_upper_bolling_lvl" : 3.2,
            "strategy_STD" : 14,
            "strategy_SMA" : 25
            }

# minutes_processed = {}
product_minutes_processed = {}
product_minute_candlestick = {}
current_tick = None
previous_tick = None
data_loaded = False
product = 'OMG-EUR'

def write_json(data,filename): 
    with open(filename,'w') as df: 
        json.dump(data, df, indent=4)

def strategy(data,buys,strategy_data):
    buy_signal = []
    sell_signal = []

    # buys = {}
    buys_not_empty_records = []
    sells_not_empty_record = []

    #money for one buy
    money = strategy_data['min_market_funds']
    value = 0
    coins = 0
    fee = 0
    earn = 0

    # limits
    min_market_funds = strategy_data['min_market_funds']
    max_buys = strategy_data['max_buys']

    for i in range(len(data['close'])):
        # check actual active buys
        buys_qty = 0
        if buys != {}: # {} dict for prtfolio [] list for anal
            for idx in list(buys.keys()):
                if buys[idx][0]['sell_flag'] == False:
                    buys_qty += 1
        #SELL-------------------------------------------------------------------------------------------------
        if data['close'][i] > data['upper'][i]: 
            # if str(data.index[i]) not in buys:
            #   buys[str(data.index[i])] = []
            #look if there are some records in buys dict
            if len(buys.keys())>=1:
                #loop over buys to        
                for idx in range(len(buys.keys())):
                #check if the buys time index is not empty and have some data
                    if buys[list(buys.keys())[idx]] != []:            
                        #prepare list of keys where are suitable sell prices
                        #also check if it is not already in the list
                        if list(buys.keys())[idx] not in sells_not_empty_record and buys[list(buys.keys())[idx]][0]['sell_flag']==False:
                            sells_not_empty_record.append(list(buys.keys())[idx])

                #after filling sells_not_empty_record list
                #loop over sells_not_empty_record
                #check BUYS dict and change sell_price to actual_sell price and remove buy_price to 0
                sell_flag = False
                for idx in sells_not_empty_record:
                    sell_price_ratio = 1.012
                    actual_sell_price = data['close'][i]

                    #search for sell_flag False nad lowest buy price !!! minimum sell ratio (sell for 6 buy for 5: 6/5=1.2 ratio)    
                    if not buys[idx][0]['sell_flag'] and actual_sell_price / buys[idx][0]['buy_price'] >= sell_price_ratio:
                        # earn = ((coins * data['close'][i]) - fee) - value
                        earnValue = buys[idx][0]['earn']
                        earnValue = earnValue + buys[idx][0]['coins'] * data['close'][i] - buys[idx][0]['fee'] - buys[idx][0]['spend_EUR']
                        buys[idx][0]['sell_flag'] = True  
                        buys[idx][0]['sell_price'] = data['close'][i]
                        buys[idx][0]['sell_time'] = str(data.index[i])
                        buys[idx][0]['earn'] = earnValue
                        earn = earn + earnValue
                        # buys[idx][0]['buy_price'] = 0
                        # buys[idx][0]['sell_time'] = buys[idx]
                        #generate sell signlas if sells_not_empty_record is not empty
                        sell_flag = True

                if sell_flag:
                    buy_signal.append(np.nan)
                    sell_signal.append(data['close'][i])
                else:
                    buy_signal.append(np.nan)
                    sell_signal.append(np.nan)

            #modify 
            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        #BUY--------------------------------------------------------------------------------------------------
        elif data['close'][i] < data['lower'][i] and buys_qty < max_buys:
            # check if there is not at leas 1x buy keys --> else buy
            if len(buys.keys()) >= 1:
                # create new key
                buys[str(data.index[i])] = [] 
                # NOW lets decide if we need to buy again !!
                # loop over non empty buys       
                for idx in range(len(buys.keys())):
                    if buys[list(buys.keys())[idx]] != []: 
                        # lets track non empty buys time indexes
                        # check if there it is not already in the list !!!
                        if list(buys.keys())[idx] not in buys_not_empty_records:
                            buys_not_empty_records.append(list(buys.keys())[idx])

                # lets process our buys_not_empty_records LIST - decide if we have to buy again
                # check last buy time
                last_buy_time = dateutil.parser.parse(str(buys_not_empty_records[-1])).timestamp()
                # check now buy time
                now_buy_time = dateutil.parser.parse(str(data.index[i])).timestamp()
                diff = int(now_buy_time) - int(last_buy_time)
                set_minimum_buy_time = 60*60
                #if time differnce is too small ---> we will not buy
                if diff < set_minimum_buy_time:
                    #only if price is better then set ratio :)
                    buy_ratio = 1.008
                    last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                    now_buy_price = data['close'][i]
                    if last_buy_price / now_buy_price > buy_ratio:
                        buy_signal.append(data['close'][i])
                        sell_signal.append(np.nan)
                        coins = (money/data['close'][i])
                        fee = (money*0.005)
                        value = value + money
                        time = str(data.index[i])
                        buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})
                    else:      
                        buy_signal.append(np.nan)
                        sell_signal.append(np.nan)
                        # if time is bigger then set ---> we can buy
                else:
                    # if time is longer than minimum buy time -> consider before price and actual price
                    # if last buy price is higher then dont buy + set MAX time to not buy !
                    buy_ratio = 1.008
                    last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                    now_buy_price = data['close'][i]
                    # during this time DONT buy if price is higher than last time
                    if last_buy_price / now_buy_price < 1 and diff < set_minimum_buy_time+(60*60):
                        buy_signal.append(np.nan)
                        sell_signal.append(np.nan)           
                    else:
                        buy_signal.append(data['close'][i])
                        sell_signal.append(np.nan)
                        coins = (money/data['close'][i])
                        fee = (money*0.005)
                        value = value + money
                        time = str(data.index[i])
                        buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})


            # DONT BUY ANYMORE AFTER 1.ST BUY        
            else:
                #create buys time key
                buys[str(data.index[i])] = [] 
                coins = (money/data['close'][i])
                fee = (money*0.005)
                # value = value + money
                time = str(data.index[i])
                buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})

                # buy signal to list for graph      
                buy_signal.append(data['close'][i])
                sell_signal.append(np.nan)

                # FINAL statement where non of the lower/upper limit match
        else:
            sell_signal.append(np.nan)
            buy_signal.append(np.nan)

    return(buy_signal,sell_signal,earn,buys,value,coins,fee)

def on_open(ws):
    print("opened connection")

    # timestamp = str(time.time())[:13]
    # message = timestamp+"GET/users/self/verify"
    # hmac_key = base64.b64decode("<API SECRET>")
    # sig = hmac.new(hmac_key, message.encode(), hashlib.sha256)
    # sig64 = base64.b64encode(sig.digest())

    # print (message)
    # print (sig64)
    # print (sig64.decode())

    subscribe_message = {
        "type": "subscribe",
        "channels":[ 
            {
                "name": "ticker",
                "product_ids":
                [
                    product
                    ]
            }
        ],

        # "signature": str(sig64.decode()),
        # "key": "<API KEY>",
        # "passphrase": "API PASSPHRASE",
        # "timestamp": timestamp
    }
    
    # print(subscribe_message)
    ws.send(json.dumps(subscribe_message))
    # pp(subscribe_message)

def product_tick(message):
    global product_minutes_processed, product_minute_candlestick
    current_tick = json.loads(message)
    previous_tick = current_tick
    current_product = current_tick['product_id'] 

    # check if folder exist
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)
    # save each product to separated folder and file
    json_data_file = datetime.now().strftime("%Y%m%d")
    json_data_file = product_folder+'/data'+current_product+json_data_file+'.json'
    if not os.path.isfile(json_data_file) or os.stat(json_data_file).st_size == 0:
        with open(json_data_file,'w') as data:
            json.dump({},data)

    # print("****recieved message****")
    # print("TICK FOR: ",current_product)
    # print ("{} {} = {}".format(current_tick['time'],current_product,current_tick['price']))
    # pp(current_tick)
    # print(current_tick)

    tick_datetime_object = dateutil.parser.parse(current_tick['time']) #save recvd time to formatable object
    tick_datetime_object = tick_datetime_object.astimezone() #convert to my timezone
    tick_dt = tick_datetime_object.strftime("%d.%m.%Y %H:%M") #format time object to custom readable

    # print("tick time data",tick_dt)

    #if product ID key is not in the dict - add key into the list
    if current_product not in product_minutes_processed:
        product_minutes_processed[current_product] =[]

    if current_product not in product_minute_candlestick:
        product_minute_candlestick[current_product] =[]

    # check if time in actual product tick is already in the dict
    if not tick_dt in product_minutes_processed[current_product]: #we have new minute
        print("starting new candlestick for",current_product)
        product_minutes_processed[current_product].append(tick_dt)
        # print (product_minutes_processed)

        if len(product_minute_candlestick[current_product])>0:
            #close price when new minute candlestick start
            one_minute = timedelta(minutes=1)
            tick_dt_m = tick_datetime_object-one_minute
            tick_dt_m = tick_dt_m.strftime("%d.%m.%Y %H:%M")
            product_minute_candlestick[current_product][-1]["close"] = previous_tick['price']#[-1] last candlestick

            # after close save data
            with open(json_data_file) as json_file:
                data = json.load(json_file)
                if current_product not in data:
                    data[current_product] =[]
                data[current_product].append(product_minute_candlestick[current_product][-1])
            write_json(data,json_data_file)

        # imprt candlesticks from file if it is empty
        if product_minute_candlestick[current_product] == []:
        # check if we have yesterday file
            yesterday_json_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            yesterday_json_data_file = product_folder+'/data'+current_product+yesterday_json_date+'.json'
            if os.path.isfile(yesterday_json_data_file) and not os.stat(yesterday_json_data_file).st_size == 0:
                # concatenate yesterday data and today
                data = json_data_merge(yesterday_json_data_file,json_data_file,current_product)
                product_minute_candlestick[current_product] = (data[current_product])
            else:
                # load to product_minute_candlestick actual data
                with open(json_data_file) as json_file:
                    data = json.load(json_file)
                    product_minute_candlestick[current_product] = (data[current_product])
                

        product_minute_candlestick[current_product].append({
            "time":tick_dt,
            "open":current_tick['price'],
            "high":current_tick['price'],
            "low":current_tick['price']
        }
        )

    if len(product_minute_candlestick[current_product][-1])>0: #if there is data in product_minute_candlestick
        # temp = product_minute_candlestick[current_product][-1] #last in the list

        if current_tick['price'] > product_minute_candlestick[current_product][-1]['high']:
            product_minute_candlestick[current_product][-1]['high'] = current_tick['price']
        if current_tick['price'] < product_minute_candlestick[current_product][-1]['low']:
            product_minute_candlestick[current_product][-1]['low'] = current_tick['price']

    # print("=======candlesticks========")
    # print(product_minute_candlestick)

    #######################################################################################
    ###################### DATA FRAME START ###############################################
    #######################################################################################

    df = pd.json_normalize(product_minute_candlestick,current_product)
    #format the collumns
    df[['open','close','high','low']] = df[['open','close','high','low']].apply(pd.to_numeric)
    df[['time']] = pd.to_datetime(df['time'],format='%d.%m.%Y %H:%M')
    df = df.set_index('time')

    # load strategy JSON
    strategy_file = product_folder+'/'+product+'-strategy.json'
    if not os.path.isfile(strategy_file) or os.stat(strategy_file).st_size == 0:
        product_info = get_product(product)
        default_strategy = {
            "strategy_lower_bolling_lvl" : 2.0,
            "strategy_upper_bolling_lvl" : 3.2,
            "strategy_STD" : 14,
            "strategy_SMA" : 26,
            "min_market_funds": float(product_info['min_market_funds']),
            "max_buys": 5,
            "base_min_size" : float(product_info['base_min_size'])
            } 
        # save default strategy
        with open(strategy_file,'w') as new_file:
            json.dump(default_strategy,new_file,indent=4)
        # load default strategy
        with open(strategy_file) as new_file:
            strategy_data = json.load(new_file)
    else:
        with open(strategy_file) as new_file:
            strategy_data = json.load(new_file)
    
    strategy_SMA = strategy_data['strategy_SMA']
    strategy_STD = strategy_data['strategy_STD']
    strategy_upper_bolling_lvl = strategy_data['strategy_upper_bolling_lvl']
    strategy_lower_bolling_lvl = strategy_data['strategy_lower_bolling_lvl']
    min_market_funds = strategy_data['min_market_funds']
    max_buys = strategy_data['max_buys']

    df['SMA'] = df['close'].rolling(window=strategy_SMA).mean()
    df['STD'] = df['close'].rolling(window=strategy_STD).std()
    df['upper'] = df['SMA'] + (df['STD'] *strategy_upper_bolling_lvl)
    df['lower'] = df['SMA'] - (df['STD'] *strategy_lower_bolling_lvl)

    period = max(strategy_SMA,strategy_STD)
    df_len = len(df)
    df_new = df[df_len-4:-1]

    print (df_new)
    print ("LowBoll:{} UppBoll:{} STD:{} SMA:{} MinFunds:{} MaxBuys:{}".format(strategy_lower_bolling_lvl,
                                                                    strategy_upper_bolling_lvl,
                                                                    strategy_STD,strategy_SMA,
                                                                    min_market_funds,
                                                                    max_buys))

    # check if product folder exist
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)

    # load product leger file (buys / sells) ----> for parsing to next strategy call
    ledger_file = product_folder+'/'+product+'buys.json'
    if not os.path.isfile(ledger_file) or os.stat(ledger_file).st_size == 0:
        # save default ledger
        with open(ledger_file,'w') as new_file:
            json.dump({},new_file)
        # load default ledger
        with open(ledger_file) as json_ledger_file:
            ledger = json.load(json_ledger_file)
    else:
        # load saved ledger
        with open(ledger_file) as json_ledger_file:
            ledger = json.load(json_ledger_file)

    # call main strategy
    strategy_return = strategy(df_new,ledger,strategy_data)

    #analyze buys - clean empty records
    clean_buys = {}
    buys = strategy_return[3]
    if buys != {}:
        for record in buys:
            if not buys[record]==[]:
                    clean_buys[record]=buys[record]    

    #save clean buys (ledger) after strategy
    if buys != {}:
        with open(ledger_file,'w') as new_file: 
            json.dump(clean_buys, new_file, indent=4)
    

def on_message(ws, message):
   
    product_tick(message)
   
def on_error(ws,mes):
    print("Error",mes)

socket = "wss://ws-feed.pro.coinbase.com"

ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_error=on_error)
ws.run_forever(ping_interval=40, ping_timeout=30)
print("end")
# ws.run_forever()
