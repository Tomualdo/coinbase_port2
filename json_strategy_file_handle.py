import json
from portfolio2 import *

def json_strategy_file_handle(current_product,product_folder):
    # load strategy JSON
    product_info = get_product(current_product)
    default_strategy = {
            "strategy_lower_bolling_lvl" : 2.6,
            "strategy_upper_bolling_lvl" : 2.2,
            "strategy_STD" : 28,
            "strategy_SMA" : 36,
            "min_market_funds": float(product_info['min_market_funds']),
            "max_buys": 6,
            "base_min_size" : float(product_info['base_min_size']),
            "min_buy_time_minutes": 60,
            "max_time_better_price":480,
            "sell_ratio": 1.02,
            "out_of_bound_sell_ratio": 1.075,
            "min_buy_time_buy_ratio":1.02,
            "min_ballance_buy": 40,
            "EUR_to_buy_size":20,
            "forced_buy":False,
            "forced_sell":False,
            "ooa_buy_size_ratio":0.3,
            "ooa_max_buys": 10,
            "ooa_sell_ratio":1.012,
            "ooa_out_of_bound_sell_ratio": 1.015,
            "ooa_min_buy_time_minutes": 30,
            "ooa_max_time_better_price":120,
            "ooa_min_buy_time_buy_ratio":1.012
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
                print("STRATEGY file difference !!!")
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