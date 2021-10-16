import requests
import os

# An example of using the service
API_URL = 'http://127.0.0.1:5000'
FOLDER = os.path.dirname(os.path.abspath(__file__))


def read_model_files(alg, name, tway):
  file, content = None, None
  # use CASA format (CASA, FastCA, medici)
  if alg in ['casa', 'fastca', 'medici']:
    file = {'model': open('files/{}-casa-{}-way.model'.format(name, tway)),
            'constraint': open('files/{}-casa-{}-way.constraint'.format(name, tway))}
  # use a single model file (ACTS, PICT, Tcases)
  elif alg in ['acts', 'pict', 'tcases']:
    file = {'model': open('files/{}-{}.model'.format(name, alg))}
  # use ACTS format (coffee4j, jcunit)
  elif alg in ['coffee4j', 'jcunit']:
    file = {'model': open('files/{}-acts.model'.format(name, alg))}
  # the content in the model file should be appended in the run command (jenny)
  elif alg == 'jenny':
    with open('files/{}-jenny-{}-way.model'.format(name, tway)) as file:
      content = file.readline().strip()

  return file, content


# required parameters
strength = 5
algorithm = 'tcases'
model = 'M41_V1'
files, model_plain = read_model_files(algorithm, model, strength)
data = {'algorithm': algorithm, 'model': model, 'timeout': 1000, 'repeat': 1,
        'strength': strength, 'model_plain': model_plain}

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
