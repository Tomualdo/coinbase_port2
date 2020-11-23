import requests
from datetime import datetime
from authorize_coinbase import *

product = 'OMG-EUR'
current_product = 'test'
coins = 9999

def push_note(title, message,API_PUSH=PUSH):
    url = 'https://api.pushbullet.com/v2/pushes'
    headers = { 'Access-Token': API_PUSH }
    data = {'title': title, 'body': message, 'type': 'note'}
    r = requests.post(url, data=data, headers=headers).json()
    print('Pushed: ' + message)

# push_note("BUY" + product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
# push_note("SELL" + product,str(coins)+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
# push_note("BUY FAIL #3 " + current_product," at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
a = 1
try:
    print(a+"t")
except Exception as e: 
    print(e)
    push_note(e," error at strategy "+current_product+" at "+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))