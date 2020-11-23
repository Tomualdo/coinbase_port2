
import os
import json

ROOT_DIR = os.path.abspath(os.curdir)

current_product = 'ZRX-EUR'

product_folder = ROOT_DIR+'/'+current_product
if not os.path.isdir(product_folder):
    os.makedirs(product_folder)

print("LEDGER LOADING "+current_product)
print("------------")
# load current_product leger file (buys / sells) ----> for parsing to next strategy call
ledger_file = product_folder+'/'+current_product+'buys.json'
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