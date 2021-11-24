class Extraction:
  """
  The functions to extract array sizes from the stdout_file of covering array generation tools.
  * integer > 0  : the size of an array
  * integer = -2 : the algorithm fails to execute
  * None         : no result is obtained
  """
  
  def __init__(self, algorithm):
    self.algorithm = algorithm
    self.switcher = {
      'acts': lambda x: self.acts(x),
      'pict': lambda x: self.pict(x),
      'cagen': lambda x: self.cagen(x),
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
    for line in console[::-1]:
      if line.startswith('Number of Tests'):
        num = line.strip().split()[-1]
        if num.isdigit():
          return int(num)
    return None
  
  @staticmethod
  def pict(console):
    if len(console) > 1:
      # for abstract model
      start_line = 0
      for line in console:
        if line.split()[0].strip().isdigit():
          break
        start_line += 1
      size = len(console) - start_line
      if size > 0:
        return size

      # for original model
      length = len(console[-1].split())
      count = 0
      for line in console[::-1]:
        if len(line.split()) == length:
          count += 1
      return count if count > 1 else None
    else:
      return None
  
  @staticmethod
  def cagen(console):
    for line in console:
      if line.startswith('size'):
        number = int(line.strip().split()[1])
        return number
      if line.find('error') > 0 or line.find('ERROR') > 0:
        return -2
    return None
    
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
          line.find('a dimension must have at least 2 features') > 0 or \
          line.find('impossible with only 0 dimensions') > 0 or \
          line.find('Argument list too long') > 0 or \
          line.find('was given twice') > 0:
        return -2
    return len(console) if len(console) > 0 else None
  
  @staticmethod
  def medici(console):
    for line in console[::-1]:
      num = line.strip().split()
      if num[0] == 'Ottenuti:' and num[1].isdigit():
        return int(num[1])
    return None
  
  @staticmethod
  def tcases(console):
    for line in console:
      # the models that tcases cannot handle
      # Can't create test case for tuple=Tuple[[p8=2, p1=2]]
      if line.find('Can\'t create test case for tuple') > 0 or line.find('Can\'t create test cases') > 0:
        return -2
      if line.startswith('java'):
        if line.find('OutOfMemoryError') > 0:
          return -9
        elif line.find('Exception') > 0 or line.find('Error') > 0:
          return -2
      
      line = line.strip().split(' - ')[-1]
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
      elif line.startswith('[Error] The expression must not evaluate to false') or \
          line.startswith('Exception in thread'):
        return -2
      elif line.startswith('[Error]'):
        return -7
    return None
  
  @staticmethod
  def jcunit(console):
    for line in console:
      if line.find('OutOfMemoryError') > 0:
        return -9
      if line.find('Too many attributes or attribute values') > 0 or \
          line.startswith('Exception in thread') or \
          line.startswith('[Error]'):
        return -2
      if line.startswith('# Array Size'):
        return int(line.strip().split()[-1])
    return None


if __name__ == '__main__':
  alg = 'pict'
  ext = Extraction(alg)
  print(ext.array_size('example/stdout/pict.origin.stdout.txt'))
