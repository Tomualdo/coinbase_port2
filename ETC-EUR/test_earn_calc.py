import json
import os
from portfolio2 import *
from pprintpp import pprint as pp
import logging

def ledger_load(current_product):
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)

    print("LEDGER LOADING..... "+current_product)
    print("-------------------")
    # load current_product leger file (buys / sells) ----> for parsing to next strategy call
    ledger_file = product_folder+'/'+current_product+'buys.json'
    with open(ledger_file) as json_ledger_file:
        ledger = json.load(json_ledger_file)
        return ledger

led = ledger_load('OMG-EUR')


   