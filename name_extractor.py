#!/usr/bin/python
# coding=UTF-8

from math import log
import os
import re
import sys
from comparator import calculate_errors
from tokenizer import Tokenizer
from trainer import Trainer
from estimator import Estimator

verbose = False

class Model():
  def __init__(self, tokenizer, estimator):
    self.tokenizer = tokenizer
    self.estimator = estimator 
    self.found_names = {}

  def extract_names(self, tkns, second_passing):
    self.found_names = {}

    tkns = [t for t in tkns if not t.tkn in ['dr', 'drs', 'drd', 'mr', 'mrs', 'ms', 'professor', 'dipl', 'prof', 'miss', 'emeritus', 'ing', 'assoc', 'asst', 'lecturer', 'ast', 'res', 'inf', 'diplom', 'jun', 'junprof', 'inform', 'lect', 'senior', 'ass', 'ajarn', 'honorarprof', 'theol', 'math', 'phil', 'doz', 'dphil']]

    i = 0
    while i <= len(tkns) - 4:
      cur_tkns = tkns[i:i+4]
      # el = cur_tkns[0].element
      # cur_tkns = [t for t in cur_tkns if t.element == el]

      full_probs = self.estimator.get_full_probs(cur_tkns, second_passing)
      index = full_probs.index(max(full_probs))
      arr = [
        'WWWW', 'WWWN', 'WWNW', 'WWNN', 'WNWW', 'WNWN', 'WNNW', 'WNNN', 
        'NWWW', 'NWWN', 'NWNW', 'NWNN', 'NNWW', 'NNWN', 'NNNW', 'NNNN',
        'Nnnn', 'NNnn', 'NNNn'
      ]
      name = " ".join([t.tkn for t in tkns[i:i+4]])
      probs = [arr[j] + str(full_probs[j]) for j in range(0,19)]
      # print "xxx", name, probs

      if index < 12: # Is word.
        tkns[i].is_name = False
        i += 1
      else:
        name_length = 2 if (index - 12 == 0) else index - 11

        if index == 16:
          tkns[i].is_name = False
          i += 1
          continue
        elif index == 17:
          name_length = 2
        elif index == 18:
          name_length = 3

        if name_length > len(cur_tkns):
          name_length = len(cur_tkns)

        name_start = int(i)
        name_end = int(i) + int(name_length)
        name_tkns = tkns[name_start:name_end]

        for tkn in name_tkns:
          tkn.is_name = True

        name_tkns = [t.tkn for t in name_tkns if re.search('[0-9]', t.tkn) == None]
        titles = ['dr', 'mr', 'mrs', 'ms', 'professor', 'dipl', 'prof', 'miss', 'emeritus', 'ing']
        name_tkns = [t for t in name_tkns if not t in titles]

        i += name_length
        if len(name_tkns) <= 1:
          continue

        if len([t for t in name_tkns if len(t) > 1]) == 0:
          continue

        name = " ".join(name_tkns).encode('utf-8')
        self.found_names[name] = full_probs[index], full_probs[0]
    return tkns

  def compare(self, x, y):
    return int((float(y[0]) - float(y[1])) - (float(x[0]) - float(x[1])))

  def print_results(self):
    for name in sorted(self.found_names, cmp=self.compare, key=self.found_names.get):
      if verbose: print name, self.found_names[name]
      else: print name

  def extract(self, filename):
    with open(filename) as f:
      html =  f.read()

      tkns = self.tokenizer.tokenize(html)
      self.estimator.calculate_tkn_incidence(tkns)
      tkns = model.extract_names(tkns, False)
      for i in range(0, 3):
        self.estimator.calculate_secondary_features(tkns)
        tkns = self.tokenizer.tokenize(html)
        tkns = model.extract_names(tkns, True)

if __name__ == "__main__":
  tokenizer = Tokenizer()
  estimator= Estimator(tokenizer)
  trainer = Trainer(tokenizer)
  estimator.load_name_cond_probs("data/probabilities/tokenized_authors_prob.txt")
  estimator.load_word_cond_probs("data/probabilities/conditional_not_a_name_prob.txt")
  estimator.load_conditional_probabilities("data/probabilities/conditional_probs_4.txt")
  model = Model(tokenizer, estimator)

  if len(sys.argv) > 1:
    if len(sys.argv) > 2 and sys.argv[2] == '-v':
      verbose = True
  
    if sys.argv[1] == 'train':
      test_path = "downloaded_pages/faculty"
      expected_path = "data/correct_names"
      file_nums = [f[-7:-4] for f in os.listdir(expected_path) if os.path.isfile(os.path.join(expected_path, f))]

      for file_num in file_nums:
        print "File", file_num
        test_file = os.path.join(test_path, file_num + ".html")
        expected_file = os.path.join(expected_path, "names_" + file_num + ".txt")
        if not os.path.isfile(test_file):
          print "Missing file", test_file
          quit()
        elif not os.path.isfile(expected_file):
          print "Missing file", expected_file
          quit()

        trainer.train(test_file, expected_file)
      trainer.compute_probabilities()
    else:
      model.extract(sys.argv[1])
      model.print_results()
  else:
    test_path = "downloaded_pages/faculty"
    expected_path = "data/correct_names"
    file_nums = [f[-7:-4] for f in os.listdir(expected_path) if os.path.isfile(os.path.join(expected_path, f))]

    type_1_errors = 0
    type_2_errors = 0
    test_names_count = 0
    expected_names_count = 0

    for file_num in file_nums:
      test_file = os.path.join(test_path, file_num + ".html")
      expected_file = os.path.join(expected_path, "names_" + file_num + ".txt")

      if not os.path.isfile(test_file):
        print "Missing file", test_file
        quit()
      elif not os.path.isfile(expected_file):
        print "Missing file", expected_file
        quit()

      model.extract(test_file)
      type_1, type_2, correct_names = calculate_errors(expected_file, model.found_names) 
      type_1_errors += len(type_1)
      type_2_errors += len(type_2)
      test_names_count += len(type_1) + len(correct_names)
      expected_names_count += len(type_2) + len(correct_names)

      print "File", test_file
      print "False positives:", len(type_1), "/", (len(type_1) + len(correct_names))
      print "False negatives:", len(type_2), "/", (len(type_2) + len(correct_names))

    print "Total false positives:", type_1_errors, "/", test_names_count, float(type_1_errors) / test_names_count
    print "Total false negatives:", type_2_errors, "/", expected_names_count, float(type_2_errors) / expected_names_count
