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



# last_buy_time = dateutil.parser.parse(str(buys_not_empty_records[-1])).timestamp()
last_buy_time = dateutil.parser.parse('2020-10-01 16:57:00').timestamp()
# check now buy time
# now_buy_time = dateutil.parser.parse(str(data.index[i])).timestamp()
now_buy_time = dateutil.parser.parse('2020-11-01 16:57:00').timestamp()
diff = int(now_buy_time) - int(last_buy_time)
print(diff)