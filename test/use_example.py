import requests
import os

# An example of using the service
FOLDER = os.path.dirname(os.path.abspath(__file__))
API_URL = 'http://127.0.0.1:5000'

# required parameters
data = {'timeout': 10, 'repeat': 2, 'strength': 2}

# required files
casa = {'model': open(os.path.join(FOLDER, 'spins_casa.citmodel'), 'rb'),
        'constraint': open(os.path.join(FOLDER, 'spins_casa.constraint'), 'rb')}

acts1 = {'model': open(os.path.join(FOLDER, 'spins_acts.model'), 'rb')}
acts2 = {'model': open(os.path.join(FOLDER, 'tcas_acts.model'), 'rb')}

fastca = {'model': open(os.path.join(FOLDER, 'gcc_casa_3_way.model'), 'rb'),
          'constraint': open(os.path.join(FOLDER, 'gcc_casa_3_way.cons'), 'rb')}

pict = {'model': open(os.path.join(FOLDER, 'spins_pict_2_way.model'), 'rb')}


r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=casa)
print(r)
print(r.json())
if r.json()['result']['best']['array'] != 'none':
  r = requests.get(API_URL + '/' + r.json()['result']['best']['array'])
  print(r.content)
  with open('result.txt', 'w') as f:
    f.write(bytes.decode(r.content))

#r = requests.post(API_URL + '/generation', data=data, files=acts2)
#print(r.json())

