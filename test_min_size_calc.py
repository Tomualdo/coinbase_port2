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
import logging
from load_candles_data import load_candle_data_days

current_product = 'OMG-EUR'

def get_calc_minSize(current_product,eur=1):
    # get last close price from data
    data = load_candle_data_days(current_product,1)
    last_price = (data[current_product][-1]['close'])
    calc = eur / float(last_price)
    return round(float(calc),2)

pp(get_calc_minSize(current_product,10))