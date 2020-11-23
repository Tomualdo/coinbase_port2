import json
import os
from portfolio2 import *
from pprintpp import pprint as pp
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logfile.log',level='DEBUG', format=log_format)

def ledger_load(current_product):
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)

    print("LEDGER LOADING..... "+current_product)
    print("-------------------")
    # load current_product leger file (buys / sells) ----> for parsing to next strategy call
    ledger_file = product_folder+'/'+current_product+'buys.json'
    if not os.path.isfile(ledger_file) or os.stat(ledger_file).st_size == 0:
        # save default empty ledger
        with open(ledger_file,'w') as new_file:
            json.dump({},new_file)
        # load default ledger
        with open(ledger_file) as json_ledger_file:
            ledger = json.load(json_ledger_file)
            return ledger
    else:
        # load saved ledger
        with open(ledger_file) as json_ledger_file:
            ledger = json.load(json_ledger_file)
    
            print(".....LEDGER LOADED "+current_product)
            print("------------------")
            return ledger