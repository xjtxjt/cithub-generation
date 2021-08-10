from datetime import datetime
from random import randrange
import re
import sys
import os
import subprocess
import signal
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
    
    # add path of executable binary
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
    
    # SPECIAL TREATMENT
    # tcases: remove 'tmp/' from the output file (the first occurrence)
    if self.parameters['algorithm'] == 'tcases':
      run = run.replace('tmp/', '', 1)
    
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
    
    # the run & clean command
    RUN = self.process_command()
    self.logger.info('> TIMEOUT = ' + self.parameters['timeout'] + ', repeat = ' + self.parameters['repeat'])

    # the result
    result = {'size': [], 'time': [], 'best': {'size': -1, 'time': -1, 'array': '', 'console': ''}}
    best_size = sys.maxsize
    best_console = ''
    best_content = ''
    
    for i in range(int(self.parameters['repeat'])):
      # randomise seed for some algorithms
      cd = RUN.replace('[SEED]', str(randrange(999999)))
      
      # if the argument list is too long (e.g., jenny)
      if len(cd) > 131072:
        self.logger.info('> Error: Argument list too long.')
        with open(console_file, 'w') as file:
          file.write('Error: Argument list too long.\n')
        return {'size': [-2], 'time': [-2], 'best': {'size': -2, 'time': -2, 'array': '', 'console': console_file}}
      
      self.logger.info('> RUN: ' + cd)
      console_out = open(console_file, 'wb')
      
      # execute the command
      start = datetime.now()
      prc = subprocess.Popen(cd, shell=True, start_new_session=True, stdout=console_out, stderr=console_out)
      
      try:
        #run_p = subprocess.run(cd.split(' '), timeout=int(self.parameters['timeout']), stdout=console_out)
        prc.communicate(timeout=int(self.parameters['timeout']))
      except subprocess.TimeoutExpired:
        self.logger.info('> Time expired at iteration {}'.format(i))
        # kill all child processes
        os.killpg(prc.pid, signal.SIGTERM)
    
      end = datetime.now()
      time = (end - start).seconds
      console_out.flush()
      console_out.close()

      # run post-process command, if there exists
      #if CLEAN is not None:
        #self.logger.info('> RUN: ' + CLEAN)
        #subprocess.run(CLEAN)
        
      # if there is no specified output file, or the output file is not produced (due to timeout),
      # then use console as the output
      if self.parameters['output_type'] == 'console' or not os.path.isfile(array_file):
        copyfile(console_file, array_file)
      
      # get size from the console file
      extract = Extraction(self.parameters['algorithm'])
      out = extract.array_size(console_file)
      # r = subprocess.run(GET_SIZE, shell=True, capture_output=True)
      # out = bytes.decode(r.stdout).strip()
      
      # cannot find an array size, no result is obtained
      if out is None or out <= 0:
        # 1) unable to execute
        if out == -2:
          self.logger.info('> Result: Unable to execute, time spent = ' + str(time))
          self.delete_files()
          return {'size': [-2], 'time': [-2], 'best': {'size': -2, 'time': -2, 'array': '', 'console': console_file}}
        # 2) terminate before timeout, runs out of memory
        #    in this case, only one repetition is needed
        elif time < int(self.parameters['timeout']) - 10:
          self.logger.info('> Result: Run out of memory, time spent = ' + str(time))
          self.delete_files()
          return {'size': [-9], 'time': [-9], 'best': {'size': -9, 'time': -9, 'array': '', 'console': console_file}}
        # 3) runs out of time
        else:
          result['size'].append(-1)
          result['time'].append(-1)
          continue
      
      # find array size
      size = int(out)
      result['size'].append(size)
      result['time'].append(time)
      
      # update the best result
      if size < best_size:
        best_size = size
        result['best']['size'] = size
        result['best']['time'] = time
        encoding = 'ISO-8859-1' if self.parameters['algorithm'] == 'medici' else 'utf-8'
        with open(console_file, 'r', encoding=encoding) as f:
          best_console = f.read()
        with open(array_file, 'r', encoding=encoding) as f:
          best_content = f.read()
    
    # end the for loop, all repetitions are finished
    self.delete_files()
    
    # save the final best array files
    if best_console != '':
      with open(console_file, 'w', encoding='utf-8') as f:
        f.writelines(best_console)
    if best_content != '':
      with open(array_file, 'w', encoding='utf-8') as f:
        f.write(best_content)
    result['best']['array'] = array_file
    result['best']['console'] = console_file
    
    return result
  
  def delete_files(self):
    # delete test model files
    #for e in ['model', 'constraint']:
    #  if e in self.parameters:
    #    os.remove(self.parameters[e])

    # SPECIAL TREATMENT
    # tcases: remove files 'tmp/XXX-Generators.json', 'tcases.log'
    if self.parameters['algorithm'] == 'tcases':
      tmp_file = self.parameters['console'].replace('.console', '-Generators.json')
      if os.path.isfile(tmp_file):
        os.remove(tmp_file)
      if os.path.isfile('tcases.log'):
        os.remove('tcases.log')
