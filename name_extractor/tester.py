# coding=UTF-8

import os
import sys
import itertools
import dataset
import exact_matching_extractor
import naive_bayesian_extractor
import nltk_extractor
import nsnb_extractor

class Tester():
  dataset = dataset.Dataset()

  def calculate_errors(self, expected_names, actual_names):
    type_1_errors = [] # False positive.
    type_2_errors = [] # False negative.
    correct_names = []
  
    expected_names_ = {}
    for n in expected_names:
      expected_names_[n] = True
  
    for n in actual_names:
      if not n in expected_names:
        type_1_errors.append(n)
      else:
        correct_names.append(n)
  
    for n in expected_names:
      if not n in actual_names:
        type_2_errors.append(n)
  
    return type_1_errors, type_2_errors, correct_names

  def cross_val(self, num_folds=5):
    Tester.dataset.load()
    fold_size = int(len(Tester.dataset.documents) / num_folds)
    if len(Tester.dataset.documents) % num_folds != 0:
      fold_size += 1

    folds = []
    for i in range(0, len(Tester.dataset.documents), fold_size):
      folds.append(Tester.dataset.documents[i:i+fold_size])

    for test_fold in range(0, num_folds):
      train_folds = [f for i, f in enumerate(folds) if i != test_fold]

      type_1_errors = 0
      type_2_errors = 0
      test_names_count = 0
      expected_names_count = 0

      # TODO: convert to Python3 and use interfaces.
      # test_extractor = exact_matching_extractor.ExactMatchingExtractor(simple_matching=True)
      # test_extractor = naive_bayesian_extractor.NaiveBayesianExtractor()
      # test_extractor = nltk_extractor.NltkExtractor()
      test_extractor = nsnb_extractor.NsnbExtractor()

      test_extractor.fit(list(itertools.chain.from_iterable(train_folds)))
      for d in folds[test_fold]:
        names = test_extractor.extract(d[1])
        expected_names = d[2]

        type_1, type_2, correct_names = self.calculate_errors(expected_names, names) 

        type_1_errors += len(type_1)
        type_2_errors += len(type_2)
        test_names_count += len(type_1) + len(correct_names)
        expected_names_count += len(type_2) + len(correct_names)

      precision = 1.0 - float(type_1_errors) / test_names_count
      recall = 1.0 - float(type_2_errors) / expected_names_count
      print precision, ',', recall

if __name__ == "__main__":
  os.chdir(os.path.dirname(__file__))

  tester = Tester()
  if len(sys.argv) > 1:
    doc = Tester.dataset.get_document(int(sys.argv[1]))
    # test_extractor = exact_matching_extractor.ExactMatchingExtractor(simple_matching=False)
    # test_extractor = naive_bayesian_extractor.NaiveBayesianExtractor()
    # test_extractor = nsnb_extractor.NsnbExtractor()
    test_extractor = nltk_extractor.NltkExtractor()
    test_extractor.fit([])
    names = test_extractor.extract(doc[1])

    print 'URL:', doc[0]
    print 'Returned names:', len(names)
    print 'Expected correct names:', len(doc[2])

    type_1, type_2, correct_names = tester.calculate_errors(doc[2], names) 
    precision = 0.0
    if len(names) > 0:
      precision = 1.0 - float(len(type_1)) / len(names)
    recall = 1.0 - float(len(type_2)) / len(doc[2])
    print 'Correct names:', len(correct_names)
    print 'Wrong names:', len(type_2)
    print 'P:', precision, ', R:', recall

    print '=============================='
    print 'False positives:'
    for n in type_1:
      print '   ', n

    print '=============================='
    print 'False negatives:'
    for n in type_2:
      print '   ', n
  else:
    tester.cross_val()
