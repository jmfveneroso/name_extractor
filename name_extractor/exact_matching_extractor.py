# coding=UTF-8

import os
import re
from math import log
import tokenizer

class ExactMatchingExtractor():
  """ 
  The naive extractor class extracts names based on a simple matching 
  strategy. It compares tokens with names extracted from a name database 
  through a single or composite matching strategy. The single matching
  strategy consists of checking if each token exists in the database,
  the composite matching strategy checks if a sequence of tokens exists in
  the database, returning the longest matching sequence.
  """
  tokenizer = tokenizer.Tokenizer()

  def __init__(self, simple_matching=True):
    self.simple_matching = simple_matching
    self.names = {}

  def fit(self, docs):
    """ 
    Loads the names from a file to a map.
    """
    directory = "../conditional_dataset"
    with open(os.path.join(directory, "names.txt")) as f:
      for line in f:
        name = line.strip()
        if self.simple_matching:
          tkns = name.split(" ")
          for t in tkns:
            self.names[t] = True
        else:
          self.names[name] = True

  def do_simple_matching(self, tkns):
    el = None
    for t in tkns:
      if not el is None and t.element != el:
        return None
      el = t.element

      if not t.tkn in self.names:
        return None
    return ' '.join([t.tkn for t in tkns])

  def do_composite_matching(self, tkns):
    el = None
    for t in tkns:
      if not el is None and t.element != el:
        return None
      el = t.element

    key = ' '.join([t.tkn for t in tkns])
    if key in self.names:
      return key
    return None

  def extract(self, html):
    """ 
    Extracts names from a list of tokens.
    """ 
    tkns = ExactMatchingExtractor.tokenizer.tokenize(html)
    names = []

    i = 0
    while i < len(tkns) - 1:
      found_name = False
      for name_size in [5, 4, 3, 2]:
        if i + name_size >= len(tkns):
          continue

        name = None
        if self.simple_matching:
          name = self.do_simple_matching(tkns[i:i+name_size])
        else:
          name = self.do_composite_matching(tkns[i:i+name_size])

        if not name is None:
          if not name in names:
            names.append(name)
          i += name_size 
          found_name = True
          break
      
      if not found_name: 
        i += 1
    return names
