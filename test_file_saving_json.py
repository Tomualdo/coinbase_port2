import json
import os
ROOT_DIR = os.path.abspath(os.curdir)

current_product = ['LOL']

def write_json(data, filename=ROOT_DIR+'/data.json'): 
    with open(filename,'a') as f: 
        json.dump(data, f, indent=4)

json_file = open(ROOT_DIR+'/data.json','r')
if list(json_file) == []:
    write_json({})
    json_file.close()
else:
    json_file.close()
        

with open(ROOT_DIR+'/data.json') as json_file:
    data = json.load(json_file)
    data['LOL'] = 'test'
write_json(data)