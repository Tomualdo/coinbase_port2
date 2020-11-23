from os import write
import websocket, json
import dateutil.parser
import json, hmac, hashlib, time, requests, base64
from pprintpp import pprint as pp
from datetime import datetime, timedelta 
import os

ROOT_DIR = os.path.abspath(os.curdir)

jsonFile = []
# minutes_processed = {}
product_minutes_processed = {}
product_minute_candlestick = {}
current_tick = None
previous_tick = None
data_loaded = False
data_added_to_candles = False


def write_json(data,filename): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)

def on_open(ws):
    print("opened connection")

    # timestamp = str(time.time())[:13]
    # message = timestamp+"GET/users/self/verify"
    # hmac_key = base64.b64decode("<API SECRET>")
    # sig = hmac.new(hmac_key, message.encode(), hashlib.sha256)
    # sig64 = base64.b64encode(sig.digest())

    # print (message)
    # print (sig64)
    # print (sig64.decode())

    subscribe_message = {
        "type": "subscribe",
        "channels":[ 
            {
                "name": "ticker",
                "product_ids":
                [
                    "BTC-EUR",
                    "ETH-EUR",
                    "OMG-EUR",
                    "XRP-EUR",
                    "BCH-EUR",
                    "LTC-EUR",
                    "EOS-EUR",
                    "XLM-EUR",
                    "XTZ-EUR",
                    "ETC-EUR",
                    "ZRX-EUR",
                    "LINK-EUR",
                    "ALGO-EUR",
                    "BAND-EUR",
                    "NMR-EUR",
                    "CGLD-EUR",
                    "UMA-EUR"]
            }
        ],

        # "signature": str(sig64.decode()),
        # "key": "<API KEY>",
        # "passphrase": "API PASSPHRASE",
        # "timestamp": timestamp
    }
    
    # print(subscribe_message)
    ws.send(json.dumps(subscribe_message))

def product_tick(message):
    global product_minutes_processed, product_minute_candlestick
    current_tick = json.loads(message)
    previous_tick = current_tick

    current_product = current_tick['product_id']

    # check if folder exist
    product_folder = ROOT_DIR+'/'+current_product
    if not os.path.isdir(product_folder):
        os.makedirs(product_folder)
    # save each product to separated folder and file
    json_data_file = datetime.now().strftime("%Y%m%d")
    json_data_file = product_folder+'/data'+current_product+json_data_file+'.json'
    if not os.path.isfile(json_data_file) or os.stat(json_data_file).st_size == 0:
        with open(json_data_file,'w') as data:
            json.dump({},data)

    # print("****recieved message****")
    # print("TICK FOR: ",current_product)
    # print ("{} {} = {}".format(current_tick['time'],current_product,current_tick['price']))
    # pp(current_tick)
    # print(current_tick)

    tick_datetime_object = dateutil.parser.parse(current_tick['time']) #save recvd time to formatable object
    tick_datetime_object = tick_datetime_object.astimezone() #convert to my timezone
    tick_dt = tick_datetime_object.strftime("%d.%m.%Y %H:%M") #format time object to custom readable

    # print("tick time data",tick_dt)

    #if product ID key is not in the dict - add key into the list
    if current_product not in product_minutes_processed:
        product_minutes_processed[current_product] =[]

    if current_product not in product_minute_candlestick:
        product_minute_candlestick[current_product] =[]

    # check if time in actual product tick is already in the dict
    if not tick_dt in product_minutes_processed[current_product]: #we have new minute
        print("starting new candlestick for",current_product)
        product_minutes_processed[current_product].append(tick_dt)
        # print (product_minutes_processed)

        if len(product_minute_candlestick[current_product])>0:
            #close price when new minute candlestick start
            one_minute = timedelta(minutes=1)
            tick_dt_m = tick_datetime_object-one_minute
            tick_dt_m = tick_dt_m.strftime("%d.%m.%Y %H:%M")
            product_minute_candlestick[current_product][-1]["close"] = previous_tick['price']#[-1] last candlestick
    
            # try to save in JSON format
            # json_file = open(ROOT_DIR+'/data'+json_data_file+'.json')
            # if list(json_file) == []:
            #     write_json({})
            #     json_file.close()
            # else:
            #     json_file.close()
            with open(json_data_file) as json_file:
                data = json.load(json_file)
                if current_product not in data:
                    data[current_product] =[]
                data[current_product].append(product_minute_candlestick[current_product][-1])
            write_json(data,json_data_file)

        # if not data_added_to_candles:
        #     minute_candlestick.append(minute_candlestick_json)
        #     data_added_to_candles = True

        product_minute_candlestick[current_product].append({
            "time":tick_dt,
            "open":current_tick['price'],
            "high":current_tick['price'],
            "low":current_tick['price']
        }
        )

    if len(product_minute_candlestick[current_product][-1])>0: #if there is data in product_minute_candlestick
        # temp = product_minute_candlestick[current_product][-1] #last in the list

        if current_tick['price'] > product_minute_candlestick[current_product][-1]['high']:
            product_minute_candlestick[current_product][-1]['high'] = current_tick['price']
        if current_tick['price'] < product_minute_candlestick[current_product][-1]['low']:
            product_minute_candlestick[current_product][-1]['low'] = current_tick['price']

    # print("=======candlesticks========")
    # print(product_minute_candlestick)

def on_message(ws, message):
   
    product_tick(message)
   
def on_error(ws,mes):
    print("Error",mes)

socket = "wss://ws-feed.pro.coinbase.com"

ws = websocket.WebSocketApp(socket,on_open=on_open,on_message=on_message,on_error=on_error)
ws.run_forever(ping_interval=70, ping_timeout=10)
print("run")
# ws.run_forever()
