
class Extraction:
  """
  The functions to extract array sizes from the console_file of covering array generation tools.
  * integer > 0  : the size of an array
  * integer = -2 : the algorithm fails to execute
  * None         : no result is obtained
  """
  def __init__(self, algorithm):
    self.algorithm = algorithm
    self.switcher = {
      'acts': lambda x: self.acts(x),
      'pict': lambda x: self.pict(x),
      'casa': lambda x: self.casa(x),
      'fastca': lambda x: self.fastca(x),
      'jenny': lambda x: self.jenny(x),
      'medici': lambda x: self.medici(x),
      'tcases': lambda x: self.tcases(x),
      'coffee4j': lambda x: self.coffee4j(x),
      'jcunit': lambda x: self.jcunit(x)
    }
  
  def array_size(self, console_file):
    # the output of medici cannot be resolved by utf-8 encoding
    encoding = 'ISO-8859-1' if self.algorithm == 'medici' else 'utf-8'
    with open(console_file, encoding=encoding) as file:
      console = file.readlines()
      
    if len(console) > 0 and console[-1].startswith('Killed'):
      return -9
    
    func = self.switcher.get(self.algorithm)
    size = func(console)
    return size
  
  @staticmethod
  def acts(console):
    if len(console) > 4 and console[-4].startswith('Number of Tests'):
      num = console[-4].strip().split()[-1]
      if num.isdigit():
        return int(num)
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
    if len(console) > 1:
      num = console[-1].strip().split()
      if len(num) == 3 and num[1].isdigit():
        return int(num[1])
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
    if len(console) > 3:
      num = console[-3].strip().split()
      if num[0] == 'Ottenuti:' and num[1].isdigit():
        return int(num[1])
      return None
  
  @staticmethod
  def tcases(console):
    for line in console:
      line = line.strip().split(' - ')[-1]
      # the models that tcases cannot handle
      # Can't create test case for tuple=Tuple[[p8=2, p1=2]]
      if line.startswith('Can\'t create test case for tuple') or line.endswith('Can\'t create test cases'):
        return -2
      # FunctionInputDef[find]: Created 29 valid test cases
      if line.endswith('valid test cases'):
        es = line.strip().split()
        if es[-5] == 'Created':
          number = int(line.strip().split()[-4])
          return number
    return None
  
  @staticmethod
  def coffee4j(console):
    for line in console:
      if line.startswith('# Array Size'):
        return int(line.strip().split()[-1])
      # the models that coffee4j cannot handle
      # size of parameter value equals one
      elif line.startswith('[Error] The expression must not evaluate to false'):
        return -2
      elif line.startswith('[Error]'):
        return -7
    return None
  
  @staticmethod
  def jcunit(console):
    for line in console:
      if line.startswith('# Array Size'):
        return int(line.strip().split()[-1])
      elif line.startswith('[Error]'):
        return -7
    return None
    
  
if __name__ == '__main__':
  alg = 'coffee4j'
  ext = Extraction(alg)
  print(ext.array_size('example/output/{}-console.txt'.format(alg)))

