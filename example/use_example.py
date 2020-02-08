import requests
import os


# An example of using CASA service
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# required parameters
#   name    : name of the test model
#   timeout : time budget (seconds)
data = {'name': 'example',
        'timeout': 50}
# required files
files = {'model': open(os.path.join(THIS_FOLDER, 'example.model'), 'rb'),
         'constraint': open(os.path.join(THIS_FOLDER, 'example.constraints'), 'rb')}
files1 = {'model': open(os.path.join(THIS_FOLDER, 'spins_casa.citmodel'), 'rb'),
          'constraint': open(os.path.join(THIS_FOLDER, 'spins_casa.constraint'), 'rb')}
# the service
API_URL = 'http://127.0.0.1:8888'

r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=files)
print(r.json())
