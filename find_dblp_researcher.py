import re 
import datetime
import os
import io
import sys
from tokenizer import Tokenizer

tokenizer = Tokenizer()
def tokenize(text):
  return tokenizer.tokenize_text(text.decode("utf-8").strip())

real_names = []
names = []
dict = {}
with open('data/dblp_authors.txt') as f:
  for line in f:
    name = line.strip()
    names.append(name)

    tkns = name.split(' ')
    for tkn in tkns:
      if not tkn in dict:
        dict[tkn] = []
      dict[tkn].append(len(names) - 1)

with open('data/authors.csv') as f:
  for line in f:
    name = line.strip()
    real_names.append(name)

def rotate_list_rgt(l):
  return l[-1:] + l[:-1]

def match_name(name_tkns, dict_name):
  tkns = dict_name.split(' ')
  for i in range(0, len(tkns)):
    tkns = rotate_list_rgt(tkns)

    if len(tkns) != len(name_tkns): return False

    match = True
    for i in range(0, len(tkns)):
      if len(name_tkns) <= i:
        match = False
        break
   
      if len(name_tkns[i]) == 1:
        if name_tkns[i][0] == tkns[i][0]:
          continue

      if name_tkns[i] == tkns[i]:
        continue
      
      match = False

    if match:
      return True

  return False

def find_dblp_researcher(name):
  tkns = tokenize(name)
  
  matches = [] 
  if tkns[0] in dict:
    for id in dict[tkns[0]]:
      dict_name = names[id]
  
      if match_name(tkns, dict_name):
        matches.append(id)
  return [(id, real_names[id]) for id in matches]
  
if __name__ == "__main__":
  while True:
    query = str(raw_input('Name:'))
    print find_dblp_researcher(query)
