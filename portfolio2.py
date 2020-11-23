import json, hmac, hashlib, time, requests, base64, os
from requests.auth import AuthBase
from pprintpp import pprint as pp
from authorize_coinbase import *
import logging

ROOT_DIR = os.path.abspath(os.curdir)


log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logfile.log', format=log_format)
logger = logging.getLogger(__name__)

# To override the default severity of logging
logger.setLevel('DEBUG')

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("mylogs.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

api_url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

def write_json(data,filename): 
    with open(filename,'w') as df: 
        json.dump(data, df, indent=4)

def get_coinbase_accounts():
    r = requests.get(api_url + 'coinbase-accounts', auth=auth) # Get a list of trading accounts from the profile of the API key.
    return r.json()

def get_profiles():
    r = requests.get(api_url + 'profiles', auth=auth) # Get a list of trading accounts from the profile of the API key.
    return r.json()

def get_profile(profile_name):
    response = get_profiles()
    id = None
    for profiles in response:
        if profiles['name'] == profile_name:
            id = profiles['id']
            break
    if id == None: return None
    r = requests.get(api_url + 'profiles/'+id, auth=auth) # Get a list of trading accounts from the profile of the API key.
    return r.json()

def get_ballance():
    response = get_account('EUR')
    return response['available']
    
def save_responses(response,product_folder,product):
    # load strategy JSON
    response_file = product_folder+'/'+product+'-responses.json'
    if not os.path.isfile(response_file) or os.stat(response_file).st_size == 0:         
        with open(response_file,'w') as new_file:
            json.dump({},new_file,indent=4)
        with open(response_file,'w') as new_file:
            data = []
            data.append(response)
            json.dump(data,new_file,indent=4)

    else:
        with open(response_file) as new_file:
            data = json.load(new_file)
            data.append(response)
        write_json(data,response_file)

def get_accounts():
    r = requests.get(api_url + 'accounts', auth=auth) # Get a list of trading accounts from the profile of the API key.
    return r.json()

def get_account(currency):
    accounts = get_accounts()
    for id in range(len(accounts)):
        if accounts[id]['currency'] == currency:
            r = requests.get(api_url + 'accounts/'+accounts[id]['id'], auth=auth)
            return r.json()

def get_account_history(currency):
    """List account activity of the API key's profile. Account activity either increases or decreases your account balance. Items are paginated and sorted latest first. See the Pagination section for retrieving additional entries after the first page."""
    accounts = get_accounts()
    for id in range(len(accounts)):
        if accounts[id]['currency'] == currency:
            r = requests.get(api_url + 'accounts/'+accounts[id]['id']+'/ledger', auth=auth)
            return r.json()    

def get_account_holds(currency):
    """List holds of an account that belong to the same profile as the API key.
    Holds are placed on an account for any active orders or pending withdraw requests.
    As an order is filled, the hold amount is updated.
    If an order is canceled, any remaining hold is removed.
    For a withdraw, once it is completed, the hold is removed."""
    accounts = get_accounts()
    for id in range(len(accounts)):
        if accounts[id]['currency'] == currency:
            r = requests.get(api_url + 'accounts/'+accounts[id]['id']+'/holds', auth=auth)
            return r.json()  

def order_limit(currency,size,price):
    """Limit order size=currency amount"""
    message = {
    "size":size,
    "price":price,
    "side":"buy",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    return r.json()

def order_market_funds(currency,funds):
    message = {
    "funds":funds,
    "side":"buy",
    "type":"market",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    response = r.json()
    id = response['id']
    r = requests.get(api_url + 'orders/'+id, auth=auth)
    return r.json()

def order_market_size(currency,size):
    message = {
    "size":size,
    "side":"buy",
    "type":"market",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    product_folder = ROOT_DIR+'/'+currency
    response = r.json()
    time.sleep(0.5)
    save_responses(response,product_folder,currency)
    return (order_market_size_(response,product_folder,currency))
    
def order_market_size_(response,product_folder,currency):
    pp(response)
    for key in list(response.keys()):
        if key == 'message':
            print("PROBLEM")
            print(response['message']+" "+currency+" BUY")           
            save_responses(response,product_folder,currency)
            return{'done_reason':False}
    id = response['id'] 
    r = requests.get(api_url + 'orders/'+id, auth=auth)   
    response = r.json() 
    pp(response)
    save_responses(response,product_folder,currency)       
    return r.json()

def order_info(id):
    r = requests.get(api_url + 'orders/'+id, auth=auth)   
    response = r.json()
    time.sleep(0.5)
    pp(response)
    return r.json()
   
def get_products():
    """Get a list of available currency pairs for trading."""
    r = requests.get(api_url + 'products', auth=auth)
    return r.json()

def get_product(currency):
    """Get market data for a specific currency pair.
    currency = 'ETH-EUR' """
    products = get_products()
    for id in range(len(products)):
        if products[id]['id'] == currency:
            r = requests.get(api_url + 'products/'+products[id]['id'], auth=auth)
            return r.json()

def get_product_bid(currency):
    """Get market data for a specific currency pair.
    currency = 'ETH-EUR' """
    products = get_products()
    for id in range(len(products)):
        if products[id]['id'] == currency:
            r = requests.get(api_url + 'products/'+products[id]['id']+"/book", auth=auth)
            return r.json()

def get_orders_list():
    """List your current open orders"""
    r = requests.get(api_url + 'orders', auth=auth)
    return r.json()

def sell_market_(currency,size):
    message = {
    "size":size,
    "side":"sell",
    "type":"market",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    return r.json()

def sell_market_size(currency,size):
    message = {
    "size":size,
    "side":"sell",
    "type":"market",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    product_folder = ROOT_DIR+'/'+currency
    response = r.json()
    return (sell_market_size_(response,product_folder,currency))
    # return r.json()

def sell_market_size_(response,product_folder,currency):

    pp(response)
    for key in list(response.keys()):
        if key == 'message':
            print("PROBLEM")
            print(response['message']+" "+currency+" SELL")
            save_responses(response,product_folder,currency)
            return{'done_reason':False}
    id = response['id']
    r = requests.get(api_url + 'orders/'+id, auth=auth)
    response = r.json()
    pp(response)
    save_responses(response,product_folder,currency)
    return r.json()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# pp(get_accounts())
# pp(order_limit('OMG-EUR',1,2.7))
# pp(order_market('OMG-EUR',0.5))
# pp(get_account("OMG"))
# pp(get_product('OMG-EUR'))
# pp(sell_market_('OMG-EUR',1))
# pp(order_market_funds('OMG-EUR',1))
# pp(get_orders_list())
# r = requests.get(api_url + 'orders/4198b629-ebbc-4e4f-a384-c530a172fb6e', auth=auth)
# pp(r.json())
# pp(sell_market_size('OMG-EUR',1))
# pp(get_product('XRP-EUR'))