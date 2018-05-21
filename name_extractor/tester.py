# coding=UTF-8

import dataset
import extractor
import itertools

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
    test_extractor = extractor.Extractor()
    names = test_extractor.extract(Tester.dataset.documents[0][1])

    fold_size = len(Tester.dataset.documents) / num_folds
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

      test_extractor = extractor.Extractor()
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
      
tester = Tester()
tester.cross_val()
