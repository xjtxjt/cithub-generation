from datetime import datetime
from random import randrange
import re
import sys
import os
import subprocess


class Generation:
  
  def __init__(self, parameters, logger):
    self.parameters = parameters
    self.logger = logger
    self.base = 'bin-local'
    
  def generation(self, binary, command, size_command):
    """
    Run the specified command to invoke the generation process.
    """
    # TODO: check if all the required parameters are presented
    # mandatory: model, timeout
    # print(self.parameters)

    # parameter: 0) path of executable binary
    command = command.replace(binary, os.path.join(self.base, binary))
    
    # parameter: 1) whether there is a constraint file
    if 'constraint' not in self.parameters:
      command = re.sub(r'\{.*\}', '', command)
    else:
      command = command.replace('{', '')
      command = command.replace('}', '')
    
    # parameter: 2) input/output files & parameters
    for par in self.parameters.keys():
      command = command.replace('[{}]'.format(par), self.parameters[par])
    
    # output file
    array_file = self.parameters['output']
    
    # get_size command
    size_cd = size_command.copy()
    for x in range(len(size_command)):
      size_cd[x] = size_cd[x].replace('[output]', array_file)
    
    # the results
    result = {'size': [], 'time': [], 'best': {'size': 0, 'time': 0, 'array': array_file}}
    best_size = sys.maxsize
    best_content = ''

    for i in range(int(self.parameters['repeat'])):
      # parameter: 3) seed
      cd = command.replace('[SEED]', str(randrange(9999)))
      self.logger.info('> run: ' + cd + ' timeout = ' + self.parameters['timeout'])

      try:
        # run
        timeout_im = int(self.parameters['timeout']) + 10     # handle FastCA's embedded timeout
        start = datetime.now()
        r = subprocess.run(cd.split(' '), timeout=timeout_im, capture_output=True)
        end = datetime.now()
        
        if self.parameters['output_type'] == 'console':
          with open(array_file, 'w') as f:
            f.write(bytes.decode(r.stdout))
            
        # get size
        r = subprocess.run(size_cd, capture_output=True)
        out = bytes.decode(r.stdout).strip().split(' ')[-1]
        size = int(out)
        time = (end - start).seconds

        # record results
        result['size'].append(size)
        result['time'].append(time)
        if size < best_size:
          best_size = size
          result['best']['size'] = size
          result['best']['time'] = time
          with open(array_file, 'r') as f:
            best_content = f.read()
          f.close()
        # delete the current output file
        os.remove(array_file)
        
      except subprocess.TimeoutExpired:
        result['size'] = [-1] * int(self.parameters['repeat'])
        result['time'] = [-1] * int(self.parameters['repeat'])
        result['best']['size'] = -1
        result['best']['time'] = -1
        result['best']['array'] = 'none'
        # delete model and constraints files
        for e in ['model', 'constraint']:
          if e in self.parameters:
            os.remove(self.parameters[e])
        return result
    
    # save the final best array file
    with open(array_file, 'w') as f:
      f.write(best_content)
    
    # delete model and constraints files
    for e in ['model', 'constraint']:
      if e in self.parameters:
        os.remove(self.parameters[e])
    
    return result

