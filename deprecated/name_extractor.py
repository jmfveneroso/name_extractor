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
        self.found_names[name] = [full_probs[0], full_probs[index]]
    return tkns

  def compare(self, x, y):
    return int((float(y[0]) - float(y[1])) - (float(x[0]) - float(x[1])))

  def print_results(self):
    # for name in self.found_names:
    for name in sorted(self.found_names, cmp=self.compare, key=self.found_names.get):
      if verbose: print name, self.found_names[name]
      else: print name

  def extract_html(self, html):
    tkns = self.tokenizer.tokenize(html)
    self.estimator.calculate_tkn_incidence(tkns)
    tkns = self.extract_names(tkns, False)
    for i in range(0, 2): 
      self.estimator.calculate_secondary_features(tkns)
      tkns = self.tokenizer.tokenize(html)
      tkns = self.extract_names(tkns, True)

  # This method is a faster version of the name extraction
  # algorithm. It is less efficient, but it is enough to serve
  # as a feature for the classifier.
  def extract_html_simple(self, html):
    tkns = self.tokenizer.tokenize(html)
    tkns = self.extract_names(tkns, False)

  def extract(self, filename):
    with open(filename) as f:
      html =  f.read()
      self.extract_html(html)

fold = 1
def create_model():
  tokenizer = Tokenizer()
  estimator= Estimator(tokenizer)
  trainer = Trainer(tokenizer)
  estimator.load_name_cond_probs("data/probabilities/tokenized_authors_prob.txt")
  estimator.load_word_cond_probs("data/probabilities/conditional_not_a_name_prob.txt")
  # estimator.load_conditional_probabilities("data/probabilities/conditional_probs_4.txt")
  estimator.load_conditional_probabilities("data/probabilities/fold_" + str(fold) + ".txt")
  model = Model(tokenizer, estimator)
  return model

if __name__ == "__main__":
  model = create_model()
  trainer = Trainer(Tokenizer())

  if len(sys.argv) > 1:
    if len(sys.argv) > 2 and sys.argv[2] == '-v':
      verbose = True
  
    if sys.argv[1] == 'train':
      test_path = "downloaded_pages/faculty"
      expected_path = "data/correct_names"
      # file_nums = [f[-7:-4] for f in os.listdir(expected_path) if os.path.isfile(os.path.join(expected_path, f))]
      file_nums = [
        '180', '197', '156', '203', '095', '052', '072', '126', '184', '086', 
        '102', '034', '007', '011', '105', '199', '182', '092', '128', '031', 
        '014', '124', '129', '050', '024', '080', '122', '076', '134', '206', 

        '067', '216', '170', '107', '174', '085', '027', '074', '049', '099', 
        '177', '127', '131', '026', '192', '123', '019', '017', '178', '036', 
        '187', '113', '098', '041', '020', '146', '001', '132', '191', '112', 

        '101', '044', '037', '155', '022', '149', '201', '008', '077', '152', 
        '161', '091', '189', '087', '114', '082', '157', '100', '120', '006', 
        '147', '106', '039', '150', '209', '053', '144', '175', '005', '159', 

        '183', '013', '118', '016', '136', '158', '162', '094', '088', '210', 
        '151', '133', '029', '166', '069', '066', '061', '045', '195', '115', 
        '176', '010', '116', '121', '015', '171', '057', '063', '207', '194', 

        # '214', '179', '135', '021', '093', '208', '004', '047', '215', '211', 
        # '025', '038', '033', '071', '190', '160', '108', '141', '096', '202', 
        # '154', '009', '023', '186', '117', '002', '111', '125', '064'
      ]

      count = 1
      for file_num in file_nums:
        print "File", file_num, count, 'of', len(file_nums)
        count += 1

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

    for i in range(1, 6):
      fold = i
      model = create_model()
 
      file_nums_fold = [
        ['180', '197', '156', '203', '095', '052', '072', '126', '184', '086', 
        '102', '034', '007', '011', '105', '199', '182', '092', '128', '031', 
        '014', '124', '129', '050', '024', '080', '122', '076', '134', '206'],

        ['067', '216', '170', '107', '174', '085', '027', '074', '049', '099', 
        '177', '127', '131', '026', '192', '123', '019', '017', '178', '036', 
        '187', '113', '098', '041', '020', '146', '001', '132', '191', '112'], 

        ['101', '044', '037', '155', '022', '149', '201', '008', '077', '152', 
        '161', '091', '189', '087', '114', '082', '157', '100', '120', '006', 
        '147', '106', '039', '150', '209', '053', '144', '175', '005', '159'], 

        ['183', '013', '118', '016', '136', '158', '162', '094', '088', '210', 
        '151', '133', '029', '166', '069', '066', '061', '045', '195', '115', 
        '176', '010', '116', '121', '015', '171', '057', '063', '207', '194'], 

        ['214', '179', '135', '021', '093', '208', '004', '047', '215', '211', 
        '025', '038', '033', '071', '190', '160', '108', '141', '096', '202', 
        '154', '009', '023', '186', '117', '002', '111', '125', '064']
      ]
      file_nums = file_nums_fold[fold - 1] 

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

        # print "File", test_file
        precision = 1.0 - float(len(type_1)) / (len(type_1) + len(correct_names))
        recall = 1.0 - float(len(type_2)) / (len(type_2) + len(correct_names))
        # print precision, ',', recall
        # print "False positives:", float(len(type_1)), '/', (len(type_1) + len(correct_names))
        # print "False negatives:", float(len(type_2)), '/', (len(type_2) + len(correct_names))

      # print "Total false positives:", type_1_errors, "/", test_names_count, float(type_1_errors) / test_names_count
      # print "Total false negatives:", type_2_errors, "/", expected_names_count, float(type_2_errors) / expected_names_count
      precision = 1.0 - float(type_1_errors) / test_names_count
      recall = 1.0 - float(type_2_errors) / expected_names_count
      print precision, ',', recall
