"""
remove all files in the data directory
"""
import os

dirPath = ["data/constrained", "data/unconstrained"]
for each in dirPath:
  fileList = os.listdir(each)
  for fileName in fileList:
    os.remove(each + "/" + fileName)
