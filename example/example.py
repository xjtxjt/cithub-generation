import requests
import os

# An example of using the service
API_URL = 'http://127.0.0.1:5000'
FOLDER = os.path.dirname(os.path.abspath(__file__))


def read_model_files(alg, name, tway):
  f1, c1 = None, None
  # use CASA format
  if alg in ['casa', 'fastca', 'medici']:
    f1 = {'model': open('files/{}-casa-{}-way.model'.format(name, tway)),
          'constraint': open('files/{}-casa-{}-way.constraint'.format(name, tway))}
  # use a single model file (their respective format)
  elif alg in ['acts', 'pict', 'tcases']:
    f1 = {'model': open('files/{}-{}.model'.format(name, alg))}
  # the content in the model file should be appended in the run command
  elif alg == 'jenny':
    with open('files/{}-jenny-{}-way.model'.format(name, tway)) as file:
      c1 = file.readline().strip()

  return f1, c1


# required parameters
strength = 2
algorithm = 'tcases'
model = 'Eshop-fm'
files, model_plain = read_model_files(algorithm, model, strength)
data = {'algorithm': algorithm, 'timeout': 30, 'repeat': 1, 'strength': strength, 'model_plain': model_plain}

r = requests.get(API_URL)
print(r.json())

r = requests.post(API_URL + '/generation', data=data, files=files)
if r.status_code == 200:
  jn = r.json()
  print(jn)

  # get files
  print('\n---------------- array ----------------')
  if jn['result']['best']['array'] != '':
    r = requests.get(API_URL + '/' + jn['result']['best']['array'])
    print(bytes.decode(r.content))
  
  print('\n---------------- console ----------------')
  if jn['result']['best']['console'] != '':
    r = requests.get(API_URL + '/' + jn['result']['best']['console'])
    print(bytes.decode(r.content))
