import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from pprintpp import pprint as pp
from authorize_coinbase import *

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
    message = {
    "size":size,
    "price":price,
    "side":"buy",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
    return r.json()

def order_market(currency,funds):
    message = {
    "funds":funds,
    "side":"buy",
    "product_id":currency}
    r = requests.post(api_url + 'orders',data=json.dumps(message), auth=auth)
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# pp(order_limit('OMG-EUR',1,2.7))
# pp(order_market('OMG-EUR',0.5))
# pp(get_account("OMG"))
pp(get_product('OMG-EUR'))