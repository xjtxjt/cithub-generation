from datetime import datetime
from random import randrange
import re
import sys
import os
import subprocess
from shutil import copyfile


class Generation:
  
  def __init__(self, parameters, logger):
    self.parameters = parameters
    self.logger = logger
    self.base = 'bin-local'
  
  def handle_command(self, binary, run, get_size):
    """
    handling command parameters
    """
    # parameter 0) path of executable binary
    run = run.replace(binary, os.path.join(self.base, binary))
    
    # parameter 1) whether there is a constraint file
    if 'constraint' not in self.parameters:
      run = re.sub(r'\{.*\}', '', run)
    else:
      run = run.replace('{', '')
      run = run.replace('}', '')
    
    # parameter 2) input/output files & other parameters
    for par in self.parameters.keys():
      run = run.replace('[{}]'.format(par), self.parameters[par])
    
    # console analysis command
    # the command will output the best array size constructed most recently
    get_size = get_size.replace('[console]', self.parameters['console'])
    
    return run, get_size

  def generation(self, binary, run, get_size):
    """
    Run the specified command to invoke the generation process.
    The method will try to apply a restrict timeout strategy for conducting comparison experiments
    """
    # TODO: check the validity of parameters
    print(self.parameters)
    
    # output & console files
    array_file = self.parameters['output']
    console_file = self.parameters['console']
    
    # the run command
    RUN, GET_SIZE = self.handle_command(binary, run, get_size)
    self.logger.info('> TIMEOUT = ' + self.parameters['timeout'] + ', repeat = ' + self.parameters['repeat'])
    self.logger.info('> GET_SIZE: ' + GET_SIZE)

    # the result
    result = {'size': [], 'time': [], 'best': {'size': -1, 'time': -1, 'array': '', 'console': ''}}
    best_size = sys.maxsize
    best_console = ''
    best_content = ''
    
    for i in range(int(self.parameters['repeat'])):
      # parameter: 3) randomise seed
      cd = RUN.replace('[SEED]', str(randrange(9999)))
      self.logger.info('> RUN:  ' + cd)
      
      console_out = open(console_file, 'w')
      start = datetime.now()
      try:
        subprocess.run(cd.split(' '),
                       timeout=int(self.parameters['timeout']),
                       stdout=console_out)
      
      except subprocess.TimeoutExpired:
        self.logger.info('Timeout Expired at iteration {}'.format(i))
      except MemoryError:
        self.logger.info('MemoryError Detected!')
        console_out.close()
        return {'size': [-9], 'time': [-9], 'best': {'size': -9, 'time': -9, 'array': '', 'console': console_file}}
      end = datetime.now()
      
      # if there is no specified output file, then use console as the output
      console_out.flush()
      if self.parameters['output_type'] == 'console':
        copyfile(console_file, array_file)
      console_out.close()
      
      # get size
      r = subprocess.run(GET_SIZE, shell=True, capture_output=True)
      out = bytes.decode(r.stdout).strip()
      
      if out == '' or out == '0' or not out.isdigit():
        # cannot find an array size, no result is obtained
        result['size'].append(-1)
        result['time'].append(-1)
        continue
      
      size = int(out)
      time = (end - start).seconds
      result['size'].append(size)
      result['time'].append(time)
      
      # update the best result
      if size < best_size:
        best_size = size
        result['best']['size'] = size
        result['best']['time'] = time
        with open(console_file, 'r') as f:
          best_console = f.read()
        if os.path.exists(array_file):
          with open(array_file, 'r') as f:
            best_content = f.read()
    
    # save the final best array files
    if best_console != '':
      with open(console_file, 'w') as f:
        f.writelines(best_console)
    if best_content != '':
      with open(array_file, 'w') as f:
        f.write(best_content)
    
    # delete model and constraints files
    # for e in ['model', 'constraint']:
    #  if e in self.parameters:
    #    os.remove(self.parameters[e])
    
    result['best']['array'] = array_file
    result['best']['console'] = console_file
    return result
