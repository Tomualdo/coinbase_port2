import json
import os
from portfolio2 import *

ROOT_DIR = os.path.abspath(os.curdir)
current_product = 'ZRX-EUR'
product_folder = ROOT_DIR+'/'+current_product


# load strategy JSON
product_info = get_product(current_product)
default_strategy = {
        "strategy_lower_bolling_lvl" : 2.6,
        "strategy_upper_bolling_lvl" : 3.2,
        "strategy_STD" : 14,
        "strategy_SMA" : 25,
        "min_market_funds": float(product_info['min_market_funds']),
        "max_buys": 5,
        "base_min_size" : float(product_info['base_min_size']),
        "max_buy_time": 60,
        "sell_ratio": 1.05
        } 
strategy_file = product_folder+'/'+current_product+'-strategy.json'
if not os.path.isfile(strategy_file) or os.stat(strategy_file).st_size == 0:
    
    
    # save default strategy
    with open(strategy_file,'w') as new_file:
        json.dump(default_strategy,new_file,indent=4)
    # load default strategy
    with open(strategy_file) as new_file:
        strategy_data = json.load(new_file)
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
        print(list_difference)
        if list_difference != []:
            # [(5, 'max_buys_'), (7, 'max_buy_time'), (13, 'max_buys'), (15, 'max_buy_time_min'), (16, 'test'), (17, 'test2')]
            # len (strategy_data)
            # 8
            # len (default_strategy)
            # 10
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
                    
                # else:
                    # strategy_data[default_list_differnece[i]] = strategy_data.pop(strategy_list_differnece[i])
                    
            
            print(strategy_data)
            print(default_strategy)

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
            print(strategy_data)    
            # save default strategy
            with open(strategy_file,'w') as new_file:
                json.dump(strategy_data,new_file,indent=4)
            # load updated strategy
            with open(strategy_file) as new_file:
                strategy_data = json.load(new_file)

    