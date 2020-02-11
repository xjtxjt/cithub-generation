import requests
import os

# An example of using the service
FOLDER = os.path.dirname(os.path.abspath(__file__))
API_URL = 'http://127.0.0.1:7001'

# required parameters
data = {'timeout': 30, 'repeat': 3, 'strength': 2}

# required files
casa = {'model': open(os.path.join(FOLDER, 'spins_casa.citmodel'), 'rb'),
        'constraint': open(os.path.join(FOLDER, 'spins_casa.constraint'), 'rb')}

acts = {'model': open(os.path.join(FOLDER, 'spins_acts_2_way.model'), 'rb')}

fastca = {'model': open(os.path.join(FOLDER, 'gcc_casa_3_way.model'), 'rb'),
          'constraint': open(os.path.join(FOLDER, 'gcc_casa_3_way.cons'), 'rb')}

pict = {'model': open(os.path.join(FOLDER, 'spins_pict_2_way.model'), 'rb')}


r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=casa)
print(r)
print(r.json())
