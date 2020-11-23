import json
import os
from numpy.core.fromnumeric import product
from pprintpp import pprint as pp
from datetime import datetime, timedelta 
import dateutil.parser


current_product = 'ETC-EUR'
products = [
        		"OMG-EUR",
                    "XRP-EUR",
                    "XTZ-EUR",
                    "UMA-EUR",
                    "CGLD-EUR",
                    "NMR-EUR",
                    "ZRX-EUR",
                    "ALGO-EUR",
                    "ETC-EUR",
                    "EOS-EUR",
                    "BAND-EUR",
                    "XLM-EUR",
                    "BCH-EUR"            
        ]

ROOT_DIR = os.path.abspath(os.curdir)

today_total = 0

def ledger_info(current_product,days=1):
    global today_total
    product_folder = ROOT_DIR+'/'+current_product
    ledger_file = product_folder+'/'+current_product+'buys.json'
    with open(ledger_file) as json_ledger_file:
        ledger = json.load(json_ledger_file)

    remain_coins = 0
    total_earn = 0
    today_earn = 0
    for records in ledger:
        if ledger[records][0]['sell_flag'] == False:
            remain_coins += ledger[records][0]['coins']
            pp(ledger[records])
        else:
            total_earn += ledger[records][0]['earn']
            # only today earn
            if ledger[records][0]['sell_time'] != 0 and dateutil.parser.parse((datetime.today()-timedelta(days=days)).strftime("%Y-%m-%d")).timestamp() < dateutil.parser.parse(ledger[records][0]['sell_time']).timestamp():
                today_earn += ledger[records][0]['earn']
    print ("{} Remaining coins = {}".format(current_product,remain_coins))
    print ("{} Total earn = {}".format(current_product,total_earn))
    print ("{} Today earn = {}".format(current_product,today_earn))
    print()
    today_total += today_earn

for prd in products:
    ledger_info(prd,0)

print(today_total)
