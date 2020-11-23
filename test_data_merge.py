from os import system
from datetime import datetime
from dateutil.relativedelta import *
import dateutil.parser
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, RadioButtons
import math
from pprintpp import pprint as pp

#data merge with duplicity check
def json_data_merge_noduplicity(older_json,newer_json,target_file):

    with open(older_json) as f:
        old = json.load(f)
    with open(newer_json) as f:
        new = json.load(f)

    mer = {}
    if 'LINK-EUR' not in mer:
        mer['LINK-EUR'] =[]

    for idx_old in range(len(old['LINK-EUR'])):
        for idx_new in range(len(new['LINK-EUR'])):
            if old['LINK-EUR'][idx_old]['time'] != new['LINK-EUR'][idx_new]['time']:
                if len(new['LINK-EUR']) == idx_new + 1 : # last record in the list
                    mer['LINK-EUR'].append(old['LINK-EUR'][idx_old])
            else:
                break
    for idx_new in range(len(new['LINK-EUR'])):
        mer['LINK-EUR'].append(new['LINK-EUR'][idx_new])

    with open(target_file,'w') as data:
                json.dump(mer,data,indent=4)

#json_data_merge_noduplicity('merge_pt1.json','merge_pt2.json','merge_pt3.json')

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

b = {}
a = json_data_merge('merge_pt1.json','merge_pt2.json','LINK-EUR')
b['LINK-EUR'] = a['LINK-EUR']
print (b)