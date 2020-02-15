from flask import Flask, request, send_from_directory
from datetime import datetime
import random
import string
import json
import os
import logging
from generation import Generation


app = Flask(__name__)

# logging
logging.basicConfig(filename='log/access.log', level=logging.INFO)

# set up customised configurations
TEMP = 'tmp'
CONFIGURATION_FILE = 'configuration/{}.json'.format(os.environ.get("CALG"))
configuration = json.load(fp=open(CONFIGURATION_FILE))
for key, value in configuration.items():
  app.config[key] = value


def parameter_process(file_prefix):
  """
  Handling request parameters based on the configuration file, and upload
  necessary files.
  """
  parameters = {}
  for each in app.config['input']:
    # determine whether the post request contains the required files,
    # and save these files in the data directory
    if each['type'] == 'file':
      if each['name'] in request.files:
        parameters[each['name']] = os.path.join(TEMP, '{}.{}'.format(file_prefix, each['name']))
        file = request.files[each['name']]
        file.save(parameters[each['name']])
    # append other parameters
    else:
      parameters[each['name']] = request.form[each['name']]
  # output
  parameters['output'] = os.path.join(TEMP, file_prefix + '.out')
  parameters['console'] = os.path.join(TEMP, file_prefix + '.console')
  parameters['output_type'] = app.config['output']['type']
  return parameters


@app.route('/')
def index():
  return configuration


@app.route('/generation', methods=['POST'])
def generation():
  """
  The generation service.
  """
  if request.method == 'POST':
    stamp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    prefix = datetime.now().isoformat(timespec='seconds') + '-' + stamp
    # pre-process of parameters
    parameters = parameter_process(prefix)
    # invoke the generation service
    service = Generation(parameters, app.logger)
    app.logger.info(parameters)
    result = service.generation(app.config['bin'], app.config['run'], app.config['get_size'])
    return {'status': 'success', 'result': result}
  

@app.route('/tmp/<path:path>')
def send_file(path):
  return send_from_directory('tmp', path)


if __name__ == '__main__':
  app.logger.info('**** Run ' + os.environ.get("CALG") + ' generation service ****')
  app.run(host="0.0.0.0")
