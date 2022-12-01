from flask import Flask, request, send_from_directory, make_response, jsonify
from datetime import datetime
import random
import string
import json
import os
import logging
from generation import Generation


app = Flask(__name__)

# set up
TOOLS_SUPPORTED = []
for subdir, dirs, files in os.walk('configuration'):
  for file in files:
    TOOLS_SUPPORTED.append(file.split('.json')[0])

BIN_DIR = 'bin' if os.environ.get('C_BIN') is None else os.environ.get('C_BIN')
TEMP_DIR = 'tmp'

for dirs in ['log', 'tmp']:
  if not os.path.isdir(dirs):
    os.mkdir(dirs)

# logging
log_file = 'log/{}-access.log'.format(datetime.now().date())
logging.basicConfig(filename=log_file, level=logging.INFO)

# load configurations
CONFIGURATION = {}
for each_tool in TOOLS_SUPPORTED:
  CONFIGURATION[each_tool] = json.load(fp=open('configuration/{}.json'.format(each_tool)))


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
    'timeout': form_data.get('timeout', '100'),
    'repeat': form_data.get('repeat', '1')
  }

  # input files
  for each in config['input']:
    # determine whether the post request contains the required files, and save these files in the tmp directory
    if each['type'] == 'file':
      filename = os.path.join(TEMP_DIR, '{}.{}'.format(file_prefix, each['name']))
      # if provided as plain text
      if each['name'] + '_text' in form_data:
        file = open(filename, 'w')
        file.write(form_data[each['name'] + '_text'])
        file.close()
        parameters[each['name']] = filename
      # if provided as a file
      elif each['name'] in file_data:
        file = file_data[each['name']]
        file.save(filename)
        parameters[each['name']] = filename
    # other non-file parameters (cannot be empty)
    else:
      if each['name'] not in form_data and each['name'] not in parameters:
        # if there is a default value
        if 'default' in each:
          parameters[each['name']] = each['default']
        else:
          return None
      if each['name'] in form_data:
        parameters[each['name']] = form_data[each['name']]
  
  # output files
  parameters['output'] = os.path.join(TEMP_DIR, file_prefix + '.array')
  parameters['stdout'] = os.path.join(TEMP_DIR, file_prefix + '.stdout')
  parameters['output_type'] = config['output']['type']
  
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
  The main generation service, which requires the following parameters:
  data = {
    'algorithm': (string, mandatory) name of generation algorithm,
    'model': (string, mandatory) name of test model,
    'strength': (int, mandatory) coverage strength,
    'timeout': (int) execution time budget, default = 100,
    'repeat': (int) number of repetitions, default = 1,
    'model_text': (string) the content of test model file,
    'constraint_text': (string) the content of constraint file
  }
  Alternatively, the test model and constraints can be provided as files:
  files = {
    'model': model_file,
    'constraint': constraint_file
  }
  """
  if request.method == 'POST':
    # configuration of specific tool
    config = CONFIGURATION[request.form['algorithm']]
    
    # prefix of temporary file: [algorithm]-[model]-[t]-way-[stamp]
    stamp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    prefix = '{}-{}-{}-way-{}'.format(request.form['algorithm'], request.form['model'], request.form['strength'], stamp)
    
    # pre-process of parameters
    parameters = parameter_process(config, request.form, request.files, prefix)
    # print("parameters是:",parameters)
    if parameters is None:
      return make_response(jsonify('please check input parameters'), 404)
      
    app.logger.info('> --------------------------parameters---------------------------------------- <')
    app.logger.info(parameters)

    # invoke the generation service
    service = Generation(parameters, app.logger, BIN_DIR)
    result = service.generation()
    # result.headers['Access-Control-Allow-Origin'] = "*"
    return {'result': result},"200",{"Access-Control-Allow-Origin":"*"}


@app.route('/tmp/<path:path>')
def send_file(path):
  if os.path.isfile(os.path.join('tmp', path)):
    return send_from_directory('tmp', path)
  else:
    return make_response(jsonify('no such file'), 404)


if __name__ == '__main__':
  app.run()
