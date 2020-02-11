import subprocess
from random import randrange

a = ["awk", "BEGIN{a=0;}/^[0-9]/{a+=1;}END{print(a)}", "pict-out.txt"]
b = ['grep', 'total size', 'fastca-out.txt']
c = ['grep', 'Number of configurations', 'acts-out.txt']
r = subprocess.run(c, capture_output=True)
print(r)
out = bytes.decode(r.stdout).split(' ')[-1]
print(int(out))

#size = int(r.stdout.strip())
#print(size)

for _ in range(10):
  print(randrange(9999))
