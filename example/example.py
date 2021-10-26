import requests


def parse_filenames(directory, algorithm, name, strength):
  model_filename, constraint_filename = None, None

  # CASA, FastCA, medici: use CASA format
  if algorithm in ['casa', 'fastca', 'medici']:
    model_filename = '{}/{}-casa-{}-way.model'.format(directory, name, strength)
    constraint_filename = '{}/{}-casa-{}-way.constraint'.format(directory, name, strength)

  # ACTS, PICT, Tcases: use their respective single model files
  elif algorithm in ['acts', 'pict', 'tcases']:
    model_filename = '{}/{}-{}.model'.format(directory, name, algorithm)

  # coffee4j, jcunit: use ACTS format
  elif algorithm in ['coffee4j', 'jcunit']:
    model_filename = '{}/{}-acts.model'.format(directory, name, algorithm)

  # jenny: use jenny format (should use plain text as the input)
  elif algorithm == 'jenny':
    model_filename = '{}/{}-jenny-{}-way.model'.format(directory, name, strength)
  
  return model_filename, constraint_filename


if __name__ == '__main__':
  # an example of using the service
  API_URL = 'http://127.0.0.1:5000'
  directory = 'models'

  r = requests.get(API_URL)
  print(r.json())
  
  # parameters required
  algorithm = 'acts'
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
    print('\n---------------- array -----------------')
    if jn['result']['best']['array'] != '':
      r = requests.get(API_URL + '/' + jn['result']['best']['array'])
      print(bytes.decode(r.content))
    
    print('\n---------------- stdout ----------------')
    if jn['result']['best']['stdout'] != '':
      r = requests.get(API_URL + '/' + jn['result']['best']['stdout'])
      print(bytes.decode(r.content))
