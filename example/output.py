import subprocess

#a = ["awk", "BEGIN{a=0;}/^[0-9]/{a+=1;}END{print(a)}", "pict-out.txt"]
#b = ['grep', 'total size', 'fastca-out.txt']
#c = ['grep', '"Number"', 'acts-out.txt']

acts = "grep 'Number of Tests' output/acts-console.txt | awk 'END {print $(NF)}'"
casa = "grep 'Met coverage with' output/casa-console.txt | awk 'END {print $(NF-1)}'"
pict = "awk 'BEGIN {a=0;} /^[0-9]/ {a+=1;} END {print(a)}' output/pict-out.txt"
fastca = "awk 'END {print $(NF-1)}' output/fastca-console.txt"

print(pict)
r = subprocess.run(pict, shell=True, capture_output=True)

out = bytes.decode(r.stdout).strip()
if out == '' or out == '0' or not out.isdigit():
  print(-1)
else:
  print(int(out))
