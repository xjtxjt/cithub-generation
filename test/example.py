import requests
import os

# An example of using the service
API_URL = 'http://127.0.0.1:5000'
FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_file(alg, name, tway):
  if alg in ['casa', 'fastca']:
    return {'model': open('files/{}-casa-{}-way.model'.format(name, tway), 'rb'),
            'constraint': open('files/{}-casa-{}-way.constraint'.format(name, tway), 'rb')}
  else:
    return {'model': open('files/{}-{}.model'.format(name, alg), 'rb')}


# required parameters
strength = 2
data = {'timeout': 10, 'repeat': 2, 'strength': strength}
files = get_file('fastca', 'grep', strength)

r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=files)
print(r)

jn = r.json()
print(jn)

# get files
print('\n---------------- array ----------------')
r = requests.get(API_URL + '/' + jn['result']['best']['array'])
print(bytes.decode(r.content))

print('\n---------------- console ----------------')
r = requests.get(API_URL + '/' + jn['result']['best']['console'])
print(bytes.decode(r.content))
