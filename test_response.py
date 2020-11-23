import json
import os

def write_json(data,filename): 
    with open(filename,'w') as df: 
        json.dump(data, df, indent=4)

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

a = {
    'created_at': '2020-10-29T18:32:38.65273Z',
    'done_at': '2020-10-29T18:32:38.664Z',
    'done_reason': 'filled',
    'executed_value': '0.7642200000000000',
    'fill_fees': '0.0038211000000000',
    'filled_size': '0.30000000',
    'funds': '0.9950200000000000',
    'id': 'ca20105a-d873-407e-9475-9a518ce883c5',
    'post_only': False,
    'product_id': 'OMG-EUR',
    'profile_id': '9a34ae8a-ff8f-4e7a-8ad3-ac3f61d2a175',
    'settled': True,
    'side': 'buy',
    'specified_funds': '1.0000000000000000',
    'status': 'done',
    'type': 'market',
}

current_product = 'OMG-EUR'
ROOT_DIR = os.path.abspath(os.curdir)
product_folder = ROOT_DIR+'/'+current_product

save_responses(a,product_folder,current_product)