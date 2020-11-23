import os
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import dateutil.parser
from numpy.core.fromnumeric import mean
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, RadioButtons
import math

ROOT_DIR = os.path.abspath(os.curdir)

strategy_lower_bolling_lvl = 2.6
strategy_upper_bolling_lvl = 3.2
strategy_STD = 14
strategy_SMA = 25

def buy_procedure(i,data,buys,buy_signal,sell_signal,money,value):
    buy_signal.append(data['close'][i])
    sell_signal.append(np.nan)
    coins = (money/data['close'][i])
    fee = (money*0.005)
    value = value + money
    time = str(data.index[i])
    buys[time].append({'buy_time':time,
                        'buy_price':data['close'][i],
                        'spend_EUR':money,
                        'coins': coins,
                        'fee': fee,
                        'sell_flag' : False,
                        'sell_price': 0,
                        'sell_time' : 0,
                        'earn':0})

def strategy(data):
    buy_signal = []
    sell_signal = []

    buys = {}
    buys_not_empty_records = []
    sells_not_empty_record = []

    # money for one buy
    money = 50
    value = 0
    coins = 0
    fee = 0
    earn = 0
    
    # limits
    max_bus = 3

    for i in range(len(data['close'])):
        #SELL-------------------------------------------------------------------------------------------------
        if data['close'][i] > data['upper'][i]: 
            # if str(data.index[i]) not in buys:
            #   buys[str(data.index[i])] = []
            #look if there are some records in buys dict
            if len(buys.keys())>=1:
                #loop over buys to        
                for idx in range(len(buys.keys())):
                #check if the buys time index is not empty and have some data
                    if buys[list(buys.keys())[idx]] != []:            
                        #prepare list of keys where are suitable sell prices
                        #also check if it is not already in the list
                        if list(buys.keys())[idx] not in sells_not_empty_record and buys[list(buys.keys())[idx]][0]['sell_flag']==False:
                            sells_not_empty_record.append(list(buys.keys())[idx])

                #after filling sells_not_empty_record list
                #loop over sells_not_empty_record
                #check BUYS dict and change sell_price to actual_sell price and remove buy_price to 0
                sell_flag = False
                for idx in sells_not_empty_record:
                    sell_price_ratio = 1.012
                    actual_sell_price = data['close'][i]

                    #search for sell_flag False nad lowest buy price !!! minimum sell ratio (sell for 6 buy for 5: 6/5=1.2 ratio)    
                    if not buys[idx][0]['sell_flag'] and actual_sell_price / buys[idx][0]['buy_price'] >= sell_price_ratio:
                        # earn = ((coins * data['close'][i]) - fee) - value
                        earnValue = buys[idx][0]['earn']
                        earnValue = earnValue + buys[idx][0]['coins'] * data['close'][i] - buys[idx][0]['fee'] - buys[idx][0]['spend_EUR']
                        buys[idx][0]['sell_flag'] = True  
                        buys[idx][0]['sell_price'] = data['close'][i]
                        buys[idx][0]['sell_time'] = str(data.index[i])
                        buys[idx][0]['earn'] = earnValue
                        earn = earn + earnValue
                        # buys[idx][0]['buy_price'] = 0
                        # buys[idx][0]['sell_time'] = buys[idx]
                        #generate sell signlas if sells_not_empty_record is not empty
                        sell_flag = True

                if sell_flag:
                    buy_signal.append(np.nan)
                    sell_signal.append(data['close'][i])
                else:
                    buy_signal.append(np.nan)
                    sell_signal.append(np.nan)

            #modify 
            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)

        #BUY--------------------------------------------------------------------------------------------------
        elif data['close'][i] < data['lower'][i]:
            # check if there is not at leas 1x buy keys --> else buy
            if len(buys.keys()) >= 1:
                # create new key
                buys[str(data.index[i])] = [] 
                # NOW lets decide if we need to buy again !!
                # loop over non empty buys       
                for idx in range(len(buys.keys())):
                    if buys[list(buys.keys())[idx]] != []: 
                        # lets track non empty buys time indexes
                        # check if there it is not already in the list !!!
                        if list(buys.keys())[idx] not in buys_not_empty_records:
                            buys_not_empty_records.append(list(buys.keys())[idx])

                # lets process our buys_not_empty_records LIST - decide if we have to buy again
                # check last buy time
                last_buy_time = dateutil.parser.parse(str(buys_not_empty_records[-1])).timestamp()
                # check now buy time
                now_buy_time = dateutil.parser.parse(str(data.index[i])).timestamp()
                diff = int(now_buy_time) - int(last_buy_time)
                set_minimum_buy_time = 60*60
                #if time differnce is too small ---> we will not buy
                if diff < set_minimum_buy_time:
                    #only if price is better then set ratio :)
                    buy_ratio = 1.008
                    last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                    now_buy_price = data['close'][i]
                    if last_buy_price / now_buy_price > buy_ratio:                        
                        buy_procedure(i,data,buys,buy_signal,sell_signal,money,value)
                    else:      
                        buy_signal.append(np.nan)
                        sell_signal.append(np.nan)
                        # if time is bigger then set ---> we can buy
                else:
                    # if time is longer than minimum buy time -> consider before price and actual price
                    # if last buy price is higher then dont buy + set MAX time to not buy !
                    buy_ratio = 1.008
                    last_buy_price = buys[buys_not_empty_records[-1]][0]['buy_price']
                    now_buy_price = data['close'][i]
                    # during this time DONT buy if price is higher than last time
                    if last_buy_price / now_buy_price < 1 and diff < set_minimum_buy_time+(60*60):
                        buy_signal.append(np.nan)
                        sell_signal.append(np.nan)           
                    else:
                        buy_procedure(i,data,buys,buy_signal,sell_signal,money,value)

            # DONT BUY ANYMORE AFTER 1.ST BUY        
            else:
                #create FIRST buys time key
                buys[str(data.index[i])] = [] 
                coins = (money/data['close'][i])
                fee = (money*0.005)
                # value = value + money
                time = str(data.index[i])
                buys[time].append({'buy_time':time, 'buy_price':data['close'][i],'spend_EUR':money, 'coins': coins, 'fee': fee, 'sell_flag' : False, 'sell_price': 0,'sell_time' : 0,'earn':0})

                # buy signal to list for graph      
                buy_signal.append(data['close'][i])
                sell_signal.append(np.nan)

                # FINAL statement where non of the lower/upper limit match
        else:
            sell_signal.append(np.nan)
            buy_signal.append(np.nan)

    return(buy_signal,sell_signal,earn,buys,value,coins,fee)


current_product = 'BTC-EUR'
product_folder = ROOT_DIR+'/'+current_product
today_date = datetime.now().strftime("%Y%m%d")
# load yesterday data file if exist
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
# check if product folder exist
today_data_file = product_folder+'/data'+current_product+today_date+'.json'
yesterday_data_file = product_folder+'/data'+current_product+yesterday_date+'.json'

# load yesterday data
if os.path.isfile(yesterday_data_file) and not os.stat(yesterday_data_file).st_size == 0:
    with open(product_folder+'/data'+current_product+yesterday_date+'.json') as yesterday_file:
            y_f = json.load(yesterday_file)
            y_f = pd.json_normalize(y_f,current_product)
else: y_f = pd.DataFrame() #empty frame

# load today data
#today_data_file = ('') # CUSTOM DATA
if os.path.isfile(today_data_file) and not os.stat(today_data_file).st_size == 0:
    with open(today_data_file) as today_file:
        # f = open('data20201028.json') # load custom data
        t_f = json.load(today_file)
        t_f = pd.json_normalize(t_f,current_product)
else:
    print("Coin ",current_product," not Found !")
    exit()

# concatinate if yesterday data exist
if not y_f.empty:    
    f = pd.concat([y_f, t_f], ignore_index=True, verify_integrity=True)
else: f = t_f


#format the collumns
f[['open','close','high','low']] = f[['open','close','high','low']].apply(pd.to_numeric)
f[['time']] = pd.to_datetime(f['time'],format='%d.%m.%Y %H:%M')
f = f.set_index('time')

# load strategy JSON
strategy_file = product_folder+'/'+current_product+'-strategy.json'
if not os.path.isfile(strategy_file) or os.stat(strategy_file).st_size == 0:
    default_strategy = {
        "strategy_lower_bolling_lvl" : 2.6,
        "strategy_upper_bolling_lvl" : 3.2,
        "strategy_STD" : 14,
        "strategy_SMA" : 25
        }
    # save default strategy
    with open(strategy_file,'w') as new_file:
        json.dump(default_strategy,new_file,indent=4)
    # load default strategy
    with open(strategy_file) as new_file:
        strategy_data = json.load(new_file)
else:
    # load strategy
    with open(strategy_file) as new_file:
        strategy_data = json.load(new_file)

strategy_SMA = strategy_data['strategy_SMA']
strategy_STD = strategy_data['strategy_STD']
strategy_upper_bolling_lvl = strategy_data['strategy_upper_bolling_lvl']
strategy_lower_bolling_lvl = strategy_data['strategy_lower_bolling_lvl']

#calculat smv simple moving average and standart deviation
# #set day period
f['SMA'] = f['close'].rolling(window=strategy_SMA).mean()
f['STD'] = f['close'].rolling(window=strategy_STD).std()
f['AVG'] = f['close'].rolling(window=len(f['close'])).mean()
# f['EMA'] = f['close'].ewm(halflife=20, adjust=True).mean()
#calculate upper bollinger band
f['upper'] = f['SMA'] + (f['STD'] *strategy_upper_bolling_lvl)
#calculate lower bollinger band
f['lower'] = f['SMA'] - (f['STD'] *strategy_lower_bolling_lvl)
period = max(strategy_SMA,strategy_STD)
new_df = f[period-1:]

#create new df wit buy sell signals
strategy_return = strategy(new_df)
new_df['buy'] = strategy_return[0]
new_df['sell'] = strategy_return[1]
earn = strategy_return[2]

#analyze buys - clean empty records
clean_buys = {}
buys = strategy_return[3]
for record in buys:
      if not buys[record]==[]:
            clean_buys[record]=buys[record]
# check remained buys 
remain_spend_EUR = 0
for rec in clean_buys:
      if not clean_buys[rec][0]['sell_flag']:
            remain_spend_EUR = remain_spend_EUR + clean_buys[rec][0]['spend_EUR']

#dump to file
with open('buys.json','w') as json_dump_file: 
  json.dump(clean_buys, json_dump_file, indent=4)

#adding shade to gpraph
fig = plt.figure(figsize=(18,9))
#add the sub plot
ax = fig.add_subplot(111)

plt.subplots_adjust(left=0.07, bottom=0.4, top=0.96)
#get values from data frame
x_axis = new_df.index
#plot shade area between low and up
l = ax.fill_between(x_axis,new_df['upper'],new_df['lower'],color='silver')
ax.plot(x_axis,new_df['close'],color='magenta',lw=2.5,label='close value')
ax.plot(x_axis,new_df['SMA'],color='blue',lw=1.5,label='SMA')
# Calculate the simple average of the data
y_mean = [np.mean(new_df['close'])]*len(new_df['close'])
ax.plot(x_axis,y_mean,color='red',lw=1.5,label='AVG',linestyle='--')
if len(new_df[new_df['buy'].notnull()])>0: #dont draw if there is no buy values - also rises error
    ax.scatter(x_axis,new_df['buy'],color='green',lw=3,label='buy',marker='^',zorder=5)
    # marker label at data point
    for i, txt in enumerate(new_df['buy']):
        ax.annotate(txt, (x_axis[i], new_df['buy'][i]),textcoords="offset points",xytext=(0,10),ha='left',alpha=0.75)
        ax.annotate(str(new_df.index[i]), (x_axis[i], new_df['buy'][i]),alpha=0.75) #time annotate
    

if len(new_df[new_df['sell'].notnull()])>0:#dont draw if there is no sell values - also rises error
    ax.scatter(x_axis,new_df['sell'],color='red',lw=3,label='sell',marker='v',zorder=5)
# plt.xticks(rotation = 45)
ax.set_title(current_product+" "+str(earn)+" "+str(remain_spend_EUR))
# ax.set_xlabel('time')
ax.set_ylabel('value')
ax.legend()
# anim = animation.FuncAnimation(fig, update, interval=10)

#test sliders
axsl1 = plt.axes([0.25, 0.0, 0.65, 0.03], facecolor='lightgoldenrodyellow')
axsl2 = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
axsl3 = plt.axes([0.25, 0.10, 0.65, 0.03], facecolor='lightgoldenrodyellow')
#upper / lower
axsl4 = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
axsl5 = plt.axes([0.25, 0.20, 0.65, 0.03], facecolor='lightgoldenrodyellow')

#slider values
sl1 = Slider(axsl1, 'sl1', 0.1, 1,) #, valstep=delta_f)
sl2 = Slider(axsl2, 'SMA', 1, 80,valstep=1, valinit=strategy_SMA)
sl3 = Slider(axsl3, 'STD', 1, 80,valstep=1, valinit=strategy_STD)
sl4 = Slider(axsl4, 'upper bollinger', 0.1, 5, valinit=strategy_upper_bolling_lvl)
sl5 = Slider(axsl5, 'lower bollinger', 0.1, 5, valinit=strategy_lower_bolling_lvl)

def get_sl1_val(val):
    # return math.exp(val)       # replace with a meaningful transformation of your parameters
    return val

def get_sl2_val(val):
    # return math.log(val)
    return val

def update(val):
    ax.cla() #clear axes
    s1 = get_sl1_val(sl1.val)      # call a transform on the slider value
    s2 = get_sl2_val(sl2.val)
    s3 = get_sl2_val(sl3.val)
    s4 = get_sl2_val(sl4.val)
    s5 = get_sl2_val(sl5.val)

    l.set_alpha(s1)
    
    new_df['SMA'] = f['close'].rolling(window=int(s2)).mean()
    new_df['STD'] = f['close'].rolling(window=int(s3)).std()
    #calculate upper bollinger band
    new_df['upper'] = new_df['SMA'] + (new_df['STD'] *s4)
    #calculate lower bollinger band
    new_df['lower'] = new_df['SMA'] - (new_df['STD'] *s5)


    ax.plot(x_axis,new_df['SMA'],color='red',lw=1.5,label='SMA',zorder=0)
    ax.fill_between(x_axis,new_df['upper'],new_df['lower'],color='green')

    #create new df wit buy sell signals
    strategy_return = strategy(new_df)
    new_df['buy'] = strategy_return[0]
    new_df['sell'] = strategy_return[1]
    earn = strategy_return[2]
    #analyze buys
    clean_buys = {}
    buys = strategy_return[3]
    for record in buys:
          if not buys[record]==[]:
                clean_buys[record]=buys[record]

    remain_spend_EUR = 0
    for rec in clean_buys:
      if not clean_buys[rec][0]['sell_flag']:
            remain_spend_EUR = remain_spend_EUR + clean_buys[rec][0]['spend_EUR']

    #dump to file
    with open('buys.json','w') as json_dump_file: 
      json.dump(clean_buys, json_dump_file, indent=4)

    #REGEN ALL AXES:------------------------------------------------------------
    ax.fill_between(x_axis,new_df['upper'],new_df['lower'],color='silver')
    ax.plot(x_axis,new_df['close'],color='magenta',lw=2.5,label='close value')
    ax.plot(x_axis,new_df['SMA'],color='blue',lw=1.5,label='SMA')
    if len(new_df[new_df['buy'].notnull()])>0: #dont draw if there is no buy values - also rises error
        ax.scatter(x_axis,new_df['buy'],color='green',lw=3,label='buy',marker='^',zorder=5)
    if len(new_df[new_df['sell'].notnull()])>0:#dont draw if there is no sell values - also rises error
        ax.scatter(x_axis,new_df['sell'],color='red',lw=3,label='sell',marker='v',zorder=5)
    # plt.xticks(rotation = 45)
    ax.set_title(current_product+" "+str(earn)+" "+str(remain_spend_EUR))
    # ax.set_xlabel('time')
    ax.set_ylabel('value')
    ax.legend()
    # anim = animation.FuncAnimation(fig, update, interval=10)

    #test sliders
    axsl1 = plt.axes([0.25, 0.0, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    axsl2 = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    axsl3 = plt.axes([0.25, 0.10, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    #upper / lower
    axsl4 = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    axsl5 = plt.axes([0.25, 0.20, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    #------------------------------------------------------------------------------

    fig.canvas.draw_idle()
    fig.canvas.flush_events()
    

sl1.on_changed(update)
sl2.on_changed(update)
sl3.on_changed(update)
sl4.on_changed(update)
sl5.on_changed(update)

# plt.ion()
picture_file = datetime.now().strftime("%Y%m%d%H%M%S")
# check if folder exist
product_folder = ROOT_DIR+'/'+current_product
if not os.path.isdir(product_folder):
    os.makedirs(product_folder)
plt.savefig(product_folder+'/'+current_product+picture_file+'.png')

plt.show()
