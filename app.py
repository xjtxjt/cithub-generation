from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import random
import string
import json
import os
import subprocess

app = Flask(__name__)

# set up customised configurations
DIR = 'workspace'
configuration = json.load(fp=open('configuration.json'))
for key, value in configuration.items():
  app.config[key] = value


def file_format(filename, stamp):
  """
  Each uploaded file is identified as FILENAME-STAMP.SUFFIX
  """
  pos = filename.rfind('.')
  return os.path.join(DIR, filename[:pos] + '-' + stamp + filename[pos:])


def file_process(stamp):
  """
  Determine whether the post request contains the required files, and save
  these files in the workspace directory.
  """
  for f in app.config['input']:
    if f['label'] not in request.files:
        return 0
    file = request.files[f['label']]
    file.save(file_format(f['file'], stamp))
  return 1


def generation_process(stamp, timeout):
  """
  Run the specified command to invoke the generation process.
  """
  result = {'size': 0, 'time': 0, 'array_file': ''}
  
  # assign the required input and output files
  cd = app.config['run']
  for f in app.config['input']:
    cd = cd.replace('[{}]'.format(f['label']), file_format(f['file'], stamp))
  cd = cd.replace('[output]', file_format(app.config['output']['file'], stamp))
  
  command = cd.split(' ')
  command[0] = os.path.join(DIR, command[0])
  
  try:
    start = datetime.now()
    r = subprocess.run(command, timeout=timeout, capture_output=True)
    end = datetime.now()
  except subprocess.TimeoutExpired:
    return 'timeout', result

  # get the size of the array
  array_file = file_format(app.config['output']['file'], stamp)
  command = app.config['output']['get_size'].replace('[output]', array_file).split(' ')
  r = subprocess.run(command, capture_output=True)
  
  result['size'] = int(r.stdout)
  result['time'] = (end - start).seconds
  result['array_file'] = array_file
  return 'success', result


@app.route('/')
def index():
  return configuration


@app.route('/generation', methods=['POST'])
def generation():
  """
  The generation service.
  """
  # upload files
  if request.method == 'POST':
    rv = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    stamp = datetime.now().isoformat(timespec='seconds') + '-' + rv
    
    if file_process(stamp) == 1:
      # invoke the generation process
      timeout = int(request.form['timeout'])
      status, result = generation_process(stamp, timeout)
      return jsonify({'status': status, 'result': result})


@app.route('/workspace/<path:path>')
def send_file(path):
  return send_from_directory('workspace', path)


if __name__ == '__main__':
  app.run(host="0.0.0.0")
