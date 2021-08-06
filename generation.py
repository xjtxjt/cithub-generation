from datetime import datetime
from random import randrange
import re
import sys
import os
import subprocess
from shutil import copyfile
from extraction import Extraction


class Generation:
  
  def __init__(self, parameters, logger, base='bin'):
    self.parameters = parameters
    self.logger = logger
    self.base = base
  
  def process_command(self):
    """
    Generate the final executable command.
    """
    binary = self.parameters['bin']
    run = self.parameters['run']
    
    # path of executable binary
    run = run.replace(binary, os.path.join(self.base, binary))
    
    # whether there is a constraint file
    if 'constraint' not in self.parameters:
      run = re.sub(r'\{.*\}', '', run)
    else:
      run = run.replace('{', '')
      run = run.replace('}', '')
    
    # input/output files & other parameters
    for par in self.parameters.keys():
      run = run.replace('[{}]'.format(par), self.parameters[par])
    
    # the command will output the best array size constructed most recently
    # get_size = get_size.replace('[console]', self.parameters['console'])
    return run

  def generation(self):
    """
    Run the specified command to invoke the generation process.
    The method will try to apply a restrict timeout strategy for conducting comparison experiments
    """
    # output array & console files
    array_file = self.parameters['output']
    console_file = self.parameters['console']
    
    # the run command
    RUN = self.process_command()
    self.logger.info('> TIMEOUT = ' + self.parameters['timeout'] + ', repeat = ' + self.parameters['repeat'])
    # self.logger.info('> GET_SIZE: ' + GET_SIZE)

    # the result
    result = {'size': [], 'time': [], 'best': {'size': -1, 'time': -1, 'array': '', 'console': ''}}
    best_size = sys.maxsize
    best_console = ''
    best_content = ''
    
    extract = Extraction(self.parameters['algorithm'])
    for i in range(int(self.parameters['repeat'])):
      # randomise seed for some algorithms
      cd = RUN.replace('[SEED]', str(randrange(999999)))
      self.logger.info('> RUN:  ' + cd)
      
      console_out = open(console_file, 'w')
      start = datetime.now()
      try:
        subprocess.run(cd.split(' '),
                       timeout=int(self.parameters['timeout']),
                       stdout=console_out)
      except subprocess.TimeoutExpired:
        self.logger.info('> Timeout expired at iteration {}'.format(i))
      
      end = datetime.now()
      time = (end - start).seconds

      # if there is no specified output file, then use console as the output
      console_out.flush()
      if self.parameters['output_type'] == 'console':
        copyfile(console_file, array_file)
      console_out.close()
      
      # get size from the console file
      out = extract.array_size(console_file)
      # r = subprocess.run(GET_SIZE, shell=True, capture_output=True)
      # out = bytes.decode(r.stdout).strip()
      
      # cannot find an array size, no result is obtained
      if out is None or out <= 0:
        # 1) unable to execute
        if out == -2:
          self.logger.info('> Unable to execute, time = ' + str(time))
          return {'size': [-2], 'time': [-2], 'best': {'size': -2, 'time': -2, 'array': '', 'console': console_file}}
        # 2) terminate before timeout, runs out of memory
        #    in this case, only one repetition is needed
        elif time < int(self.parameters['timeout']) - 10:
          self.logger.info('> Run out of memory, time = ' + str(time))
          return {'size': [-9], 'time': [-9], 'best': {'size': -9, 'time': -9, 'array': '', 'console': console_file}}
        # 3) runs out of time
        else:
          result['size'].append(-1)
          result['time'].append(-1)
          continue
      # find an array size
      size = int(out)
      result['size'].append(size)
      result['time'].append(time)
      
      # update the best result
      if size < best_size:
        best_size = size
        result['best']['size'] = size
        result['best']['time'] = time
        with open(console_file, 'r') as f:
          best_console = f.read()
        with open(array_file, 'r') as f:
          best_content = f.read()
    
    # save the final best array files
    if best_console != '':
      with open(console_file, 'w') as f:
        f.writelines(best_console)
    if best_content != '':
      with open(array_file, 'w') as f:
        f.write(best_content)
        
    result['best']['array'] = array_file
    result['best']['console'] = console_file
    
    # delete model and constraints files uploaded
    for e in ['model', 'constraint']:
      if e in self.parameters:
        os.remove(self.parameters[e])
    
    return result
