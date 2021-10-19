import requests
import os


def parse_filenames(directory, algorithm, name, strength):
  model_file, constraint_file = None, None
  # use CASA format (CASA, FastCA, medici)
  if algorithm in ['casa', 'fastca', 'medici']:
    model_file = '{}/{}-casa-{}-way.model'.format(directory, name, strength)
    constraint_file = '{}/{}-casa-{}-way.constraint'.format(directory, name, strength)
  # use a single model file (ACTS, PICT, Tcases)
  elif algorithm in ['acts', 'pict', 'tcases']:
    model_file = '{}/{}-{}.model'.format(directory, name, algorithm)
  # use ACTS format (coffee4j, jcunit)
  elif algorithm in ['coffee4j', 'jcunit']:
    model_file = '{}/{}-acts.model'.format(directory, name, algorithm)
  # the content in the model file should be appended in the run command (jenny)
  elif algorithm == 'jenny':
    model_file = '{}/{}-jenny-{}-way.model'.format(directory, name, strength)
  
  return model_file, constraint_file


if __name__ == '__main__':
  # an example of using the service
  API_URL = 'http://127.0.0.1:5000'
  directory = 'models'

  r = requests.get(API_URL)
  print(r.json())
  
  # parameters required
  algorithm = 'casa'
  name = 'aircraft'
  strength = 2

  model_file, constraint_file = parse_filenames(directory, algorithm, name, strength)
  data = {'algorithm': algorithm, 'model': name, 'strength': strength}
  
  # option 1: use plain text as the input
  data['model_text'] = open(model_file).read()
  if constraint_file is not None:
    data['constraint_text'] = open(constraint_file).read()
  r = requests.post(API_URL + '/generation', data=data)
  
  # option 2: use files as the input
  # files = {'model': open(model_file)}
  # if constraint_file is not None:
  #   files['constraint'] = open(constraint_file)
  # r = requests.post(API_URL + '/generation', data=data, files=files)

  # results
  jn = r.json()
  print(jn)
  
  if r.status_code == 200:
    print('\n---------------- array ----------------')
    if jn['result']['best']['array'] != '':
      r = requests.get(API_URL + '/' + jn['result']['best']['array'])
      print(bytes.decode(r.content))
    
    print('\n---------------- stdout ----------------')
    if jn['result']['best']['stdout'] != '':
      r = requests.get(API_URL + '/' + jn['result']['best']['stdout'])
      print(bytes.decode(r.content))
