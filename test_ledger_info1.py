import json
import os
from numpy.core.fromnumeric import product
from pprintpp import pprint as pp
from datetime import datetime, timedelta 
import dateutil.parser
import sys

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
                    "BCH-EUR",
                    "BTC-EUR",
                    "LINK-EUR",
                    "LTC-EUR"

        ]

ROOT_DIR = os.path.abspath(os.curdir)

today_total = 0
dic={}
dic_spend_EUR={}
dic_spend_EUR_ooa={}
dic_spend_total={}
dic_coins={}

def ledger_info(current_product,days=0):
    global today_total
    global dic
    product_folder = ROOT_DIR+'/'+current_product
    if os.path.isfile(product_folder+'/'+current_product+'buys.json'):
        pass
    else:
        return
    ledger_file = product_folder+'/'+current_product+'buys.json'
    with open(ledger_file) as json_ledger_file:
        ledger = json.load(json_ledger_file)

    remain_coins = 0
    total_earn = 0
    today_earn = 0
    remain_spend = 0
    remain_spend_ooa = 0
    
    for records in ledger:
        if ledger[records][0]['sell_flag'] == False:
            remain_coins += ledger[records][0]['coins']
            if  'ooa_buy' in ledger[records][0] and ledger[records][0]['ooa_buy']:
                remain_spend_ooa += ledger[records][0]['spend_EUR']
            else:
                remain_spend += ledger[records][0]['spend_EUR']
            # pp(ledger[records])
        else:
            total_earn += ledger[records][0]['earn']
            # only today earn
            if ledger[records][0]['sell_time'] != 0 and dateutil.parser.parse((datetime.today()-timedelta(days=days)).strftime("%Y-%m-%d")).timestamp() < dateutil.parser.parse(ledger[records][0]['sell_time']).timestamp():
                today_earn += ledger[records][0]['earn']
    # print ("{} Remaining coins = {}".format(current_product,remain_coins))
    # print ("{} Total earn = {}".format(current_product,total_earn))
    # print ("{} {} days earn = {}".format(current_product,days,today_earn))
    dic[current_product] = today_earn
    dic_spend_EUR[current_product] = remain_spend
    dic_spend_EUR_ooa[current_product] = remain_spend_ooa
    dic_spend_total[current_product] = remain_spend + remain_spend_ooa
    dic_coins[current_product] = remain_coins
    # print()
    
    today_total += today_earn


for prd in products:
    if len(sys.argv) > 1:
        days = int((sys.argv[1]))
        ledger_info(prd,days)
    else:
        ledger_info(prd)
        days = 0


# dic = {k: v for k, v in sorted(dic.items(), key=lambda item: item[1])}
dic = sorted(dic.items(), key=lambda x: x[1])
print("EARN:")
pp(dic)

dic_spend_EUR = sorted(dic_spend_EUR.items(),key=lambda x:x[1])
print("SPEND:")
pp(dic_spend_EUR)

dic_spend_EUR_ooa = sorted(dic_spend_EUR_ooa.items(),key=lambda x:x[1])
print("SPEND OOA:")
pp(dic_spend_EUR_ooa)

dic_spend_total = sorted(dic_spend_total.items(),key=lambda x:x[1])
print("SPEND TOTAL:")
pp(dic_spend_total)

dic_coins = sorted(dic_coins.items(),key=lambda x:x[1])
print("COINS:")
pp(dic_coins)

print("Days {} total earn is: {} eur".format(days,today_total))
