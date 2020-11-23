import threading
import time
from portfolio2 import *
import continuous_threading

current_product = 'OMG-EUR'

# t_price = 3
# act = 0
# while t_price >= act:
#     act = get_product_bid('OMG-EUR')
#     act = act['bids'][0][0]
#     time.sleep(1)

actual_sell_price = 3

def selling():
    for seq in range(10):
        #check best bid
        bid = get_product_bid(current_product)
        print("best bid is {}".format(bid))
        bid = float(bid['bids'][0][0])
        if bid < actual_sell_price:
            print("bid {} did not match. try again ...{}".format(bid,seq))
            time.sleep(1)
        else:
            print("bid {} is OK  --- SELL STARTED".format(bid))
            ready_to_sell = True
            break


th = continuous_threading.Thread(target=selling)
th.start()


while 1:
    print("im runnug...")
    time.sleep(0.5)