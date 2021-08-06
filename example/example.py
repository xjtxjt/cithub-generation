import requests
import os

# An example of using the service
API_URL = 'http://127.0.0.1:5000'
FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_file(alg, name, tway):
  f, mp = None, None
  if alg == 'casa' or alg == 'fastca':
    f = {'model': open('files/{}-casa-{}-way.model'.format(name, tway), 'rb'),
         'constraint': open('files/{}-casa-{}-way.constraint'.format(name, tway), 'rb')}
  elif alg == 'acts' or alg == 'pict':
    f = {'model': open('files/{}-{}.model'.format(name, alg), 'rb')}
  elif alg == 'jenny':
    with open('files/{}-jenny-{}-way.model'.format(name, tway)) as file:
      mp = file.readline().strip()
  
  return f, mp


# required parameters
strength = 2
algorithm = 'jenny'
files, model_plain = get_file(algorithm, 'spins', strength)
data = {'algorithm': algorithm, 'timeout': 60, 'repeat': 2, 'strength': 2, 'model_plain': model_plain}

r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=files)
jn = r.json()
print(jn)

# get files
print('\n---------------- array ----------------')
r = requests.get(API_URL + '/' + jn['result']['best']['array'])
print(bytes.decode(r.content))

print('\n---------------- console ----------------')
r = requests.get(API_URL + '/' + jn['result']['best']['console'])
print(bytes.decode(r.content))
