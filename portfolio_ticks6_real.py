from logging import exception
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
from load_candles_data import load_candle_data_days
from ledger_load import ledger_load
import logging

# logging.basicConfig(filename='logfile.log', level=logging.INFO)

# log_format = "%(asctime)s::%(levelname)s::%(name)s::"\
#              "%(filename)s::%(lineno)d::%(message)s"
# logging.basicConfig(filename='logfile.log',level='DEBUG', format=log_format)

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logfile.log',level='INFO', format=log_format)
logger = logging.getLogger(__name__)

# To override the default severity of logging
logger.setLevel('DEBUG')

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("mylogs.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)

ROOT_DIR = os.path.abspath(os.curdir)

def push_note(title, message,API_PUSH=PUSH):
    url = 'https://api.pushbullet.com/v2/pushes'
    headers = { 'Access-Token': API_PUSH }
    data = {'title': title, 'body': message, 'type': 'note'}
    r = requests.post(url, data=data, headers=headers).json()
    print('Pushed: ' + message)

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

def get_calc_minSize(current_product,eur=1):
    # get last close price from data
    data = load_candle_data_days(current_product,1)
    last_price = (data[current_product][-1]['close'])
    calc = eur / float(last_price)
    return round(float(calc),2)

def json_strategy_file_handle(current_product,product_folder):
    # load strategy JSON
    product_info = get_product(current_product)
    default_strategy = {
            "strategy_lower_bolling_lvl" : 2.6,
            "strategy_upper_bolling_lvl" : 2.2,
            "strategy_STD" : 28,
            "strategy_SMA" : 36,
            "min_market_funds": float(product_info['min_market_funds']),
            "max_buys": 5,
            "base_min_size" : float(product_info['base_min_size']),
            "min_buy_time_minutes": 60,
            "max_time_better_price":480,
            "sell_ratio": 1.012,
            "out_of_bound_sell_ratio": 1.075,
            "min_buy_time_buy_ratio":1.008,
            "min_ballance_buy": 20,
            "EUR_to_buy_size":1
            }
    strategy_file = product_folder+'/'+current_product+'-strategy.json'
    if not os.path.isfile(strategy_file) or os.stat(strategy_file).st_size == 0:
    
        # save default strategy
        with open(strategy_file,'w') as new_file:
            json.dump(default_strategy,new_file,indent=4)
        # load default strategy
        with open(strategy_file) as new_file:
            strategy_data = json.load(new_file)
            return strategy_data
    else:
        with open(strategy_file) as new_file:
            strategy_data = json.load(new_file)
            # check if file contain all default keys
            # fill loaded keys
            loaded_strategy_keys = []
            for key in strategy_data.keys():
                loaded_strategy_keys.append(key)
            # fill default keys
            default_strategy_keys = []
            for key in default_strategy.keys():
                default_strategy_keys.append(key)

            #get difference
            # list_difference = [i for i in loaded_strategy_keys + default_strategy_keys if i not in loaded_strategy_keys or i not in default_strategy_keys]
            list_difference = [(i,j) for i,j in enumerate(loaded_strategy_keys + default_strategy_keys) if j not in loaded_strategy_keys or j not in default_strategy_keys]

            # print(list_difference)
            if list_difference != []:
                # separate which difference from which key
                strategy_list_differnece = []
                default_list_differnece = []
                for tup in list_difference:
                    if tup[0] < len(strategy_data):
                        strategy_list_differnece.append(tup[1])
                    if tup[0] > len(strategy_data):
                        default_list_differnece.append(tup[1])
                print(strategy_list_differnece)
                print(default_list_differnece)
                
                for i in range(len(strategy_list_differnece)):
                    # search diff and destroy if is strategy longer than def:
                    if strategy_list_differnece != [] and default_list_differnece != [] :
                        strategy_data[default_list_differnece[i]] = strategy_data.pop(strategy_list_differnece[i])
                        del strategy_list_differnece[i]
                        del default_list_differnece[i]
                        
                for i in range(len(strategy_list_differnece)):        
                    if len(strategy_data) > len(default_strategy):
                        del strategy_data[strategy_list_differnece[i]]
     
                # add new keys
                loaded_strategy_keys = []
                for key in strategy_data.keys():
                    loaded_strategy_keys.append(key)

                # fill default keys
                default_strategy_keys = []
                for key in default_strategy.keys():
                    default_strategy_keys.append(key)
                list_difference = [i for i in loaded_strategy_keys + default_strategy_keys if i not in loaded_strategy_keys or i not in default_strategy_keys]
                for i in list_difference:
                    strategy_data[i] = default_strategy[i]
                  
                # save default strategy
                with open(strategy_file,'w') as new_file:
                    json.dump(strategy_data,new_file,indent=4)

                # load updated strategy
                with open(strategy_file) as new_file:
                    strategy_data = json.load(new_file)
                    return strategy_data
            else:
                return strategy_data
    

# minutes_processed = {}
product_minutes_processed = {}
product_minute_candlestick = {}
current_tick = None
previous_tick = None
data_loaded = False
# product = 'OMG-EUR,XRP-EUR' # try to change for more product ( " OMG-EUR,BTC-EUR... " )

def write_json(data,filename): 
    with open(filename,'w') as df: 
        json.dump(data, df, indent=4)

def strategy(data,strategy_data,current_product):

    # check if current_product folder exist
    # product_folder = ROOT_DIR+'/'+current_product
    # if not os.path.isdir(product_folder):
    #     os.makedirs(product_folder)

    # print("LEDGER LOADING..... "+current_product)
    # print("-------------------")
    # # load current_product leger file (buys / sells) ----> for parsing to next strategy call
    # ledger_file = product_folder+'/'+current_product+'buys.json'
    # if not os.path.isfile(ledger_file) or os.stat(ledger_file).st_size == 0:
    #     # save default ledger
    #     with open(ledger_file,'w') as new_file:
    #         json.dump({},new_file)
    #     # load default ledger
    #     with open(ledger_file) as json_ledger_file:
    #         ledger = json.load(json_ledger_file)
    # else:
    #     # load saved ledger
    #     with open(ledger_file) as json_ledger_file:
    #         ledger = json.load(json_ledger_file)
    # buys = ledger
    # print(".....LEDGER LOADED "+current_product)
    # print("------------------")

    buys = ledger_load(current_product)

    buy_signal = []
    sell_signal = []

    # buys = {} #LEDGER !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
    base_min_size = strategy_data['base_min_size']
    min_buy_time_minutes = strategy_data['min_buy_time_minutes']
    max_time_better_price = strategy_data['max_time_better_price']
    min_buy_time_buy_ratio = strategy_data['min_buy_time_buy_ratio']
    min_ballance_buy = strategy_data['min_ballance_buy']
    EUR_to_buy_size = strategy_data['EUR_to_buy_size']

    #calculate how big size is worth of EUR
    calc_buy_size = get_calc_minSize(current_product,EUR_to_buy_size)
    print("Calculated size for {} EUR is {} {}".format(EUR_to_buy_size,calc_buy_size,current_product))

    sell_out_of_bounds = False

    there_was_buy_or_sell = False

    # main Loop
    for i in range(len(data['close'])):

        # check actual active buys
        buys_qty = 0
        if buys != {}: # {} dict for prtfolio [] list for anal
            for idx in list(buys.keys()):
                if buys[idx][0]['sell_flag'] == False:
                    buys_qty += 1
        print("ACTUAL BUYS = "+str(buys_qty))

        # First try to sell without signal ony if price over specific ratio:
        if len(buys.keys())>=1:
            #loop over buys to        
            for idx in range(len(buys.keys())):
            #check if the buys time index is not empty and have some data
                if buys[list(buys.keys())[idx]] != []:            
                    #prepare list of keys where are suitable sell prices
                    #also check if it is not already in the list
                    if list(buys.keys())[idx] not in sells_not_empty_record and buys[list(buys.keys())[idx]][0]['sell_flag']==False:
                        sells_not_empty_record.append(list(buys.keys())[idx])
            # print("Sell not epty:")
            # pp(sells_not_empty_record)
            if sells_not_empty_record != []:
                for idx in sells_not_empty_record:
                    sell_out_of_bounds_price_ratio = 1.075 # ratio for buy sell 
                    actual_sell_price = data['close'][i]
                    if buys[idx][0]['sell_flag'] != True and actual_sell_price / buys[idx][0]['buy_price'] >= sell_out_of_bounds_price_ratio:
                        sell_out_of_bounds = True
                        print("SELL OUT OF BOUNDS !!!!!!!!!!!!!!!")


        #SELL-------------------------------------------------------------------------------------------------
        if data['close'][i] > data['upper'][i] or sell_out_of_bounds: 
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
                if sells_not_empty_record == []:
                    break
                for idx in sells_not_empty_record:
                    # minimu for fee cashback is 1.005
                    sell_price_ratio = 1.012
                    actual_sell_price = data['close'][i]

                    #search for sell_flag False nad lowest buy price !!! minimum sell ratio (sell for 6 buy for 5: 6/5=1.2 ratio)    
                    if not buys[idx][0]['sell_flag'] and actual_sell_price / buys[idx][0]['buy_price'] >= sell_price_ratio:
                        # sell how much coins are in the ledger data ['coins']
                        sell_size = buys[idx][0]['coins']
                        # earn = ((coins * data['close'][i]) - fee) - value
                        push_note("SELL " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        sell_response = sell_market_size(current_product,sell_size)
                        if sell_response['done_reason'] == 'filled':
                            earnValue = buys[idx][0]['earn']
                            # earnValue = earnValue + buys[idx][0]['coins'] * data['close'][i] - buys[idx][0]['fee'] - buys[idx][0]['spend_EUR']
                            earnValue = earnValue + float(sell_response['executed_value']) - float(sell_response['fill_fees']) - buys[idx][0]['spend_EUR']

                            buys[idx][0]['sell_flag'] = True  
                            # buys[idx][0]['sell_price'] = data['close'][i]
                            buys[idx][0]['sell_price'] = float(sell_response['executed_value'])
                            buys[idx][0]['sell_time'] = str(data.index[i])
                            buys[idx][0]['earn'] = earnValue
                            earn = earn + earnValue
                            # buys[idx][0]['buy_price'] = 0
                            # buys[idx][0]['sell_time'] = buys[idx]
                            #generate sell signlas if sells_not_empty_record is not empty
                            sell_flag = True
                            there_was_buy_or_sell = True
                            push_note("SELL " + current_product,str(sell_size)+" earn: "+str(earnValue)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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
        elif data['close'][i] < data['lower'][i] and buys_qty < max_buys and min_ballance_buy < float(get_ballance()) and  data['close'][i] < data['C-AVG'][i]:
            logger.warning(" wanna buy "+current_product)
            # check if there is not at leas 1x buy keys --> else buy
            if len(buys.keys()) >= 1:
                # if ledger key (time) == data frame index (time)
                if list(buys.keys())[i] == str(data.index[i]): # this mean we got tick with already bought product
                    break
                # create new key with TIME --->from data frame
                buys[str(data.index[i])] = [] 
                # NOW lets decide if we need to buy again !!
                # loop over non empty buys       
                for idx in range(len(buys.keys())):
                    if buys[list(buys.keys())[idx]] != [] and buys[list(buys.keys())[idx]][0]['sell_flag']==False: 
                        # lets track non empty buys time indexes
                        # check if there it is not already in the list !!!
                        if list(buys.keys())[idx] not in buys_not_empty_records:
                            buys_not_empty_records.append(list(buys.keys())[idx])
                pp(buys_not_empty_records)
                if buys_not_empty_records == []:
                    # BUY if there are no active buys (everything is sold...)
                    logger.warning(" 4 -BUY with emppty list "+current_product+" "+str(buys))
                    there_was_buy_or_sell = True
                    #create buys time key
                    buys[str(data.index[i])] = []
                    push_note("BUY 4" + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    buy_response = order_market_size(current_product,calc_buy_size) #REAL
                    if buy_response['done_reason'] == 'filled':
                        # coins = (money/data['close'][i])
                        coins = float(buy_response['filled_size']) # REAL
                        # fee = (money*0.005)
                        fee = float(buy_response['fill_fees']) #REAL
                        # value = value + money
                        # coins = (money/data['close'][i])
                        # fee = (money*0.005)
                        # value = value + money
                        time = str(data.index[i])
                        # buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})
                        buys[time].append({'buy_time':time,
                                            'buy_price': float(buy_response['executed_value']) / float(buy_response['filled_size']),
                                            'spend_EUR':float(buy_response['executed_value']),
                                            'coins': coins,
                                            'fee': fee,
                                            'sell_flag' : False,
                                            'sell_price': 0,
                                            'sell_time' : 0,
                                            'earn':0}) #REAL
                        logger.warning(" 4 -AFTER BUYS APPEND "+current_product+" "+str(buys))
                        push_note("BUY " + current_product,str(coins)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    else:
                        # failed buy ?
                        push_note("BUY FAIL #4 " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                else: # ledger have buys whith flag False
                    # lets process our buys_not_empty_records LIST - decide if we have to buy again
                    # check last buy time
                    last_buy_time = dateutil.parser.parse(str(buys_not_empty_records[-1])).timestamp()
                    # check now buy time
                    now_buy_time = dateutil.parser.parse(str(data.index[i])).timestamp()
                    diff = int(now_buy_time) - int(last_buy_time)
                    set_minimum_buy_time = 60*min_buy_time_minutes
                    #if time differnce is too small ---> we will not buy
                    if diff < set_minimum_buy_time and diff != 0 and buys_not_empty_records != []:
                        #only if price is better then set ratio :)
                        buy_ratio = min_buy_time_buy_ratio
                        last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                        now_buy_price = data['close'][i]
                        if last_buy_price / now_buy_price > buy_ratio:
                            logger.warning(" 1 -BEFORE BUYS APPEND "+current_product+" "+str(buys))
                            there_was_buy_or_sell = True
                            buy_signal.append(data['close'][i])
                            sell_signal.append(np.nan)
                            push_note("BUY 1" + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            buy_response = order_market_size(current_product,calc_buy_size) #REAL
                            if buy_response['done_reason'] == 'filled':
                                # coins = (money/data['close'][i])
                                coins = float(buy_response['filled_size']) # REAL
                                # fee = (money*0.005)
                                fee = float(buy_response['fill_fees']) #REAL
                                # value = value + money
                                time = str(data.index[i])
                                # buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})
                                buys[time].append({'buy_time':time,
                                            'buy_price': float(buy_response['executed_value']) / float(buy_response['filled_size']),
                                            'spend_EUR':float(buy_response['executed_value']),
                                            'coins': coins,
                                            'fee': fee,
                                            'sell_flag' : False,
                                            'sell_price': 0,
                                            'sell_time' : 0,
                                            'earn':0}) #REAL
                                push_note("BUY " + current_product,str(coins)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                logger.warning(" 1 -AFTER BUYS APPEND "+current_product+" "+str(buys))
                            else:
                                # failed buy ?
                                push_note("BUY FAIL #1 " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        else:      
                            buy_signal.append(np.nan)
                            sell_signal.append(np.nan)
                            # if time is bigger then set ---> we can buy
                    elif buys_not_empty_records != []:
                        # if time is longer than minimum buy time -> consider before price and actual price
                        # if last buy price is higher then dont buy + set MAX time to not buy !
                        # buy_ratio = 1.008
                        last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                        now_buy_price = data['close'][i]
                        # during this time DONT buy if price is higher than last time
                        # diff != 0 ---> prevent buy multiple times in one minute
                        if last_buy_price / now_buy_price < 1 and diff < set_minimum_buy_time+(60*max_time_better_price) and diff != 0:
                            buy_signal.append(np.nan)
                            sell_signal.append(np.nan)           
                        else:
                            logger.warning(" 2 -BEFORE BUYS APPEND "+current_product+" "+str(buys))
                            there_was_buy_or_sell = True
                            buy_signal.append(data['close'][i])
                            sell_signal.append(np.nan)
                            push_note("BUY 2" + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            buy_response = order_market_size(current_product,calc_buy_size) #REAL
                            if buy_response['done_reason'] == 'filled':
                                # coins = (money/data['close'][i])
                                coins = float(buy_response['filled_size']) # REAL
                                # fee = (money*0.005)
                                fee = float(buy_response['fill_fees']) #REAL
                                # value = value + money
                                time = str(data.index[i])
                                # buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})
                                buys[time].append({'buy_time':time,
                                            'buy_price': float(buy_response['executed_value']) / float(buy_response['filled_size']),
                                            'spend_EUR':float(buy_response['executed_value']),
                                            'coins': coins,
                                            'fee': fee,
                                            'sell_flag' : False,
                                            'sell_price': 0,
                                            'sell_time' : 0,
                                            'earn':0}) #REAL
                                push_note("BUY " + current_product,str(coins)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                logger.warning(" 2 -AFTER BUYS APPEND "+current_product+" "+str(buys))
                            else:
                                # failed buy ?
                                push_note("BUY FAIL #2 " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            # No buys yes so lets buy
            # DONT BUY ANYMORE AFTER 1.ST BUY        
            else:
                logger.warning(" 3 -BEFORE BUYS APPEND "+current_product+" "+str(buys))
                there_was_buy_or_sell = True
                #create buys time key
                buys[str(data.index[i])] = []
                push_note("BUY 3" + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                buy_response = order_market_size(current_product,calc_buy_size) #REAL
                if buy_response['done_reason'] == 'filled':
                    # coins = (money/data['close'][i])
                    coins = float(buy_response['filled_size']) # REAL
                    # fee = (money*0.005)
                    fee = float(buy_response['fill_fees']) #REAL
                    # value = value + money
                    # coins = (money/data['close'][i])
                    # fee = (money*0.005)
                    # value = value + money
                    time = str(data.index[i])
                    # buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})
                    buys[time].append({'buy_time':time,
                                        'buy_price': float(buy_response['executed_value']) / float(buy_response['filled_size']),
                                        'spend_EUR':float(buy_response['executed_value']),
                                        'coins': coins,
                                        'fee': fee,
                                        'sell_flag' : False,
                                        'sell_price': 0,
                                        'sell_time' : 0,
                                        'earn':0}) #REAL
                    logger.warning(" 3 -AFTER BUYS APPEND "+current_product+" "+str(buys))
                    push_note("BUY " + current_product,str(coins)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    # failed buy ?
                    push_note("BUY FAIL #3 " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # buy signal to list for graph      
                buy_signal.append(data['close'][i])
                sell_signal.append(np.nan)

                # FINAL statement where non of the lower/upper limit match
        else:
            sell_signal.append(np.nan)
            buy_signal.append(np.nan)
    if there_was_buy_or_sell :
        logger.info(" BEFORE RETURN "+current_product+" "+str(buys))
    return(buy_signal,sell_signal,earn,buys,value,coins,fee,there_was_buy_or_sell)

def robot(product_minute_candlestick,current_product,product_folder):

    print("THE LATEST record loaded {}".format(product_minute_candlestick[current_product][0]['time']))
    print("THE MOST RECENT record loaded {}".format(product_minute_candlestick[current_product][-1]['time']))

    df = pd.json_normalize(product_minute_candlestick,current_product)
    #format the collumns
    df[['open','close','high','low']] = df[['open','close','high','low']].apply(pd.to_numeric)
    df[['time']] = pd.to_datetime(df['time'],format='%d.%m.%Y %H:%M')
    df = df.set_index('time')



    ######################################################
    ############ LOAD STRATEGY FILE ######################
    ######################################################
    strategy_data = json_strategy_file_handle(current_product,product_folder)
    
    strategy_SMA = strategy_data['strategy_SMA']
    strategy_STD = strategy_data['strategy_STD']
    strategy_upper_bolling_lvl = strategy_data['strategy_upper_bolling_lvl']
    strategy_lower_bolling_lvl = strategy_data['strategy_lower_bolling_lvl']
    min_market_funds = strategy_data['min_market_funds']
    max_buys = strategy_data['max_buys']
    base_min_size = strategy_data['base_min_size']

    df['SMA'] = df['close'].rolling(window=strategy_SMA).mean()
    df['STD'] = df['close'].rolling(window=strategy_STD).std()
    df['upper'] = df['SMA'] + (df['STD'] *strategy_upper_bolling_lvl)
    df['lower'] = df['SMA'] - (df['STD'] *strategy_lower_bolling_lvl)
    # df['AVG'] = [np.mean(df['close'])]*len(df['close'])
    df['C-AVG'] = df['close'].expanding(min_periods=4).mean() # cumulative AVERAGE

    period = max(strategy_SMA,strategy_STD)
    df_len = len(df)
    df_new = df[df_len-2:-1] # show only pre-last data frame row

    print (df_new)
    print ("{} LowBoll:{} \
    UppBoll:{} \
    STD:{} \
    SMA:{} \
    MinFunds:{} \
    MaxBuys:{} \
    EUR_one_buy:{}".format(current_product,
                        strategy_lower_bolling_lvl,
                        strategy_upper_bolling_lvl,
                        strategy_STD,strategy_SMA,
                        min_market_funds,
                        max_buys,
                        strategy_data['EUR_to_buy_size']))
    print("------------")
    
    # check if current_product folder exist
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)

    # print("LEDGER LOADING "+current_product)
    # print("------------")
    # # load current_product leger file (buys / sells) ----> for parsing to next strategy call
    ledger_file = product_folder+'/'+current_product+'buys.json'
    # if not os.path.isfile(ledger_file) or os.stat(ledger_file).st_size == 0:
    #     # save default ledger
    #     with open(ledger_file,'w') as new_file:
    #         json.dump({},new_file)
    #     # load default ledger
    #     with open(ledger_file) as json_ledger_file:
    #         ledger = json.load(json_ledger_file)
    # else:
    #     # load saved ledger
    #     with open(ledger_file) as json_ledger_file:
    #         ledger = json.load(json_ledger_file)
    # buys = ledger

    ######################################################
    ############ STRATEGY RUN ############################
    ######################################################
    print("STRATEGY CALL for "+current_product)
    print("------------")
    try:
        strategy_return = strategy(df_new,strategy_data,current_product)
    except Exception as e: 
        print(e)
        push_note(e," error at strategy "+current_product+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        exit()

    print("STRATEGY FINISH for "+current_product)
    print("------------------------------------------------------------------------")
    print()
    ######################################################
    ############ LEDGER SAVE  ############################
    ######################################################
    #analyze buys - clean empty records
    if strategy_return[7]:
        try:
            clean_buys = {}
            buys = strategy_return[3] 
            if buys != {}:
                for record in buys:
                    if not buys[record]==[]:
                            clean_buys[record]=buys[record]    
            logger.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" CLEAN "+current_product+" "+str(clean_buys))
            #save clean buys (ledger) after strategy
            if clean_buys != {}:
                with open(ledger_file,'w') as new_file: 
                    json.dump(clean_buys, new_file, indent=4)
                print("LEDGER SAVED "+current_product)
                print("-----------------------------------------------------------------------------------------------------------")   
        except Exception as e: 
            print(e)
        

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
                    "OMG-EUR",
                    "XRP-EUR",
                    "XTZ-EUR",
                    "UMA-EUR",
                    "CGLD-EUR",
                    "NMR-EUR",
                    "ZRX-EUR",
                    "ALGO-EUR",
                    "ETC-EUR"
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

def on_message(ws, message):

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
            # one_minute = timedelta(minutes=1)
            # tick_dt_m = tick_datetime_object-one_minute
            # tick_dt_m = tick_dt_m.strftime("%d.%m.%Y %H:%M")
            product_minute_candlestick[current_product][-1]["close"] = previous_tick['price']#[-1] last candlestick

            # after close save data
            with open(json_data_file) as json_file:
                data = json.load(json_file)
                if current_product not in data:
                    data[current_product] =[]
                data[current_product].append(product_minute_candlestick[current_product][-1])
            write_json(data,json_data_file)
            ###################################################
            ###############  CALL ROBOT  ###################
            try:
                robot(product_minute_candlestick,current_product,product_folder)
            except Exception as e: 

                print(e)         

        # imprt candlesticks from file if it is empty
        if product_minute_candlestick[current_product] == []:
        # check if we have yesterday file
            yesterday_json_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            yesterday_json_data_file = product_folder+'/data'+current_product+yesterday_json_date+'.json'
            if os.path.isfile(yesterday_json_data_file) and not os.stat(yesterday_json_data_file).st_size == 0:
                # concatenate yesterday data and today
                # data = json_data_merge(yesterday_json_data_file,json_data_file,current_product)
                print("LOADING stored data...")
                data = load_candle_data_days(current_product,3)
                product_minute_candlestick[current_product] = (data[current_product])
                print("...LOADING stored data COMPLETE")
                # print the latest and most recent data
                print("THE LATEST record loaded {}".format(product_minute_candlestick[current_product][0]))
                print("THE MOST RECENT record loaded {}".format(product_minute_candlestick[current_product][-1]))
                print()
            else:
                # load to product_minute_candlestick actual data
                try:
                    with open(json_data_file) as json_file:
                        data = json.load(json_file)
                        product_minute_candlestick[current_product] = (data[current_product])
                except Exception as e:
                    print(e)
                
        

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
    




def on_error(ws,mes):
    print("Error",mes)

socket = "wss://ws-feed.pro.coinbase.com"

ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_error=on_error)
while True:
    push_note("robot start"," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    ws.run_forever(ping_interval=40, ping_timeout=30)
    print("end")
    push_note("robot is off"," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
# ws.run_forever()
