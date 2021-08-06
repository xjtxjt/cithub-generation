
class Extraction:
  """
  The functions to extract array sizes from the console_file of covering array generation tools.
  * integer > 0  : the size of an array
  * integer = -2 : the algorithm fails to execute
  * None         : no result is obtained
  """
  def __init__(self, algorithm):
    self.algorithm = algorithm
  
  def array_size(self, console_file):
    with open(console_file) as file:
      console = file.readlines()
    
    switcher = {
      'acts': lambda: self.acts(console),
      'pict': lambda: self.pict(console),
      'casa': lambda: self.casa(console),
      'fastca': lambda: self.fastca(console),
      'jenny': lambda: self.jenny(console),
      'medici': lambda: self.medici(console)
    }
  
    func = switcher.get(self.algorithm)
    size = func()
    return size
  
  @staticmethod
  def acts(console):
    for line in console:
      if line.startswith('Number of Tests	:'):
        number = int(line.strip().split()[-1])
        return number
    return None

  @staticmethod
  def pict(console):
    return len(console) - 1 if len(console) > 1 else None
  
  @staticmethod
  def casa(console):
    for line in console[::-1]:
      if line.startswith('Met coverage with'):
        number = int(line.strip().split()[-2])
        return number
    return None
    
  @staticmethod
  def fastca(console):
    num = console[-1].strip().split()
    if len(num) == 3 and num[1].isdigit():
      return int(num[1])
    else:
      return None
  
  @staticmethod
  def jenny(console):
    for line in console:
      # the models that jenny cannot handle
      if line.startswith('Could not cover tuple') or \
         line.startswith('jenny: a dimension must have at least 2 features'):
        return -2
    return len(console) if len(console) > 0 else None
  
  @staticmethod
  def medici(console):
    for line in console[::-1]:
      if line.startswith('Ottenuti:'):
        number = int(line.strip().split()[-2])
        return number
    return None
    

if __name__ == '__main__':
  alg = 'medici'
  ext = Extraction(alg)
  print(ext.array_size('example/output/{}-console.txt'.format(alg)))

