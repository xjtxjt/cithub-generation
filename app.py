from flask import Flask, request, send_from_directory
from datetime import datetime
import random
import string
import json
import os
import logging
from generation import Generation


app = Flask(__name__)

# set up
TOOLS_SUPPORTED = ['acts', 'pict', 'casa', 'fastca', 'jenny', 'medici', 'tcases', 'coffee4j', 'jcunit']
BIN_DIR = 'bin' if os.environ.get('BIN') is None else os.environ.get('BIN')
TEMP_DIR = 'tmp'

# logging
log_file = 'log/{}-access.log'.format(datetime.now().date())
logging.basicConfig(filename=log_file, level=logging.INFO)

# load configurations
CONFIGURATION = {}
for each_tool in TOOLS_SUPPORTED:
  CONFIGURATION[each_tool] = {}
  conf = json.load(fp=open('configuration/{}.json'.format(each_tool)))
  for key, value in conf.items():
    CONFIGURATION[each_tool][key] = value


def parameter_process(config, form_data, file_data, file_prefix):
  """
  Handling request parameters based on the configuration file, and upload necessary files.
  :param config : the configuration of specific algorithm
  :param form_data : the form data of the request
  :param file_data : the file data of the request
  :param file_prefix : the prefix of the temporary file
  """
  parameters = {
    'algorithm': form_data['algorithm'],
    'bin': config['bin'],
    'run': config['run'],
    'timeout': form_data['timeout'],
    'repeat': form_data['repeat']
  }
  
  # input files
  for each in config['input']:
    # determine whether the post request contains the required files,
    # and save these files in the data directory
    if each['type'] == 'file':
      if each['name'] in file_data:
        parameters[each['name']] = os.path.join(TEMP_DIR, '{}.{}'.format(file_prefix, each['name']))
        file = file_data[each['name']]
        file.save(parameters[each['name']])
    # append other parameters
    else:
      parameters[each['name']] = form_data[each['name']]
  
  # output files
  parameters['output'] = os.path.join(TEMP_DIR, file_prefix + '.out')
  parameters['console'] = os.path.join(TEMP_DIR, file_prefix + '.console')
  parameters['output_type'] = config['output']['type']
  
  # post process
  if 'clean' in config.keys():
    parameters['clean'] = config['clean']
  
  return parameters


@app.route('/', methods=['GET'])
def index():
  return {'tools supported': TOOLS_SUPPORTED}


@app.route('/tool', methods=['GET'])
def tool_information():
  tool = request.args.get('name')
  return CONFIGURATION[tool]


@app.route('/generation', methods=['POST'])
def generation():
  """
  The main generation service, which require the following parameters (with examples):
  * data = {'algorithm': 'acts', 'model': 'apache', 'timeout': 60, 'repeat': 2, 'strength': 2, 'model_plain': None}
  * files = {'model': model_file, 'constraint': constraint_file}
  """
  if request.method == 'POST':
    # configuration of specific tool
    config = CONFIGURATION[request.form['algorithm']]
    
    # prefix of temporary file: [algorithm]-[model]-[t]-way-[stamp]
    stamp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    prefix = '{}-{}-{}-way-{}'.format(request.form['algorithm'], request.form['model'], request.form['strength'], stamp)
    
    # pre-process of parameters
    parameters = parameter_process(config, request.form, request.files, prefix)
    app.logger.info('> ------------------------------------------------------------------ <')
    app.logger.info(parameters)

    # invoke the generation service
    service = Generation(parameters, app.logger, BIN_DIR)
    result = service.generation()
    return {'status': 'success', 'result': result}


@app.route('/tmp/<path:path>')
def send_file(path):
  if os.path.isfile(os.path.join('tmp', path)):
    return send_from_directory('tmp', path)
  else:
    return 'None'


if __name__ == '__main__':
  app.run(host="0.0.0.0")
