import requests
import subprocess
import time
import sys


class EXP:
  
  def __init__(self, container, benchmark, algorithm, tway, repeat, port, timeout=600):
    self.container = container
    self.benchmark = benchmark
    self.algorithm = algorithm
    self.tway = tway
    self.repeat = repeat
    self.timeout = timeout
    self.port = port

  def create_container(self):
    command = 'docker run -d -p [host]:6000 -e CALG=[algorithm] --memory=16G --cpus=1 --name=[algorithm][host] waynedd/cithub-generation'
    command = command.replace('[algorithm]', str(self.algorithm))
    command = command.replace('[host]', str(self.port))
    r = subprocess.run(command.split(' '), capture_output=True)
    print('Create docker container at port ' + str(self.port) + ': ' + bytes.decode(r.stdout))
    time.sleep(5)
  
  def post_request(self, name):
    """
    the post request
    """
    data = {'strength': self.tway, 'repeat': self.repeat, 'timeout': self.timeout}
    # get the files
    model_path = 'benchmark/{}/{}-way/{}_{}_{}_way.model'.format(self.algorithm, self.tway, name, self.algorithm, self.tway)
    constraint_path = 'benchmark/{}/{}-way/{}_{}_{}_way.cons'.format(self.algorithm, self.tway, name, self.algorithm, self.tway)
    if self.benchmark == 'constrained':
      if self.algorithm in ['casa', 'fastca']:
        files = {'model': open(model_path, 'rb'), 'constraint': open(constraint_path, 'rb')}
      else:
        files = {'model': open(model_path, 'rb')}
    else:
      files = {'model': open(model_path, 'rb')}

    base_url = 'http://127.0.0.1:{}'.format(self.port)
    #r = requests.get(base_url)
    r = requests.post(base_url + '/generation', data=data, files=files)
    return r.json()
  
  def run(self):
    """
    run a given algorithm under each of the models included in the benchmark file
    """
    # create container if required
    if self.container == 'new':
      self.create_container()
      
    # for each test model
    with open(self.benchmark, 'r') as file:
      for name in file.readlines():
        name = name.strip()
        if name == '#':
          break
        
        data = self.post_request(name)
        print('> ' + name + ': ' + data['result']['best']['array'])
        # write to data file
        for indicator in ['size', 'time']:
          output = 'data/{}/{}-{}-{}-way.{}.txt'.format(self.benchmark, self.algorithm, name, self.tway, indicator)
          with open(output, 'a') as file:
            content = '[{}] {}'.format(name, ' '.join(map(str, data['result'][indicator])))
            file.write(content + '\n')
            

if __name__ == '__main__':
  # python3 exp.py [constrained] [casa] [tway] repeat=[10] port=[7001]
  args = sys.argv
  exp = EXP('use', 'constrained', 'casa', 2, 3, 7001)
  exp.run()
