#!/usr/bin/python
# coding=UTF-8

import sys
import io
import os
from tokenize_text import tokenize_text

def tokenize(text):
  return (" ".join(tokenize_text(text.decode("utf-8").strip()))).strip()

def calculate_errors(expected_names_file, test_names):
  type_1_errors = [] # False positive.
  type_2_errors = [] # False negative.
  correct_names = []

  expected_names = {}
  with open(expected_names_file) as f:
    for line in f:
      expected_names[tokenize(line)] = True

  for name in test_names:
    if not name in expected_names:
      type_1_errors.append(name)
    else:
      correct_names.append(name)

  for name in expected_names:
    if not name in test_names:
      type_2_errors.append(name)

  return type_1_errors, type_2_errors, correct_names

if __name__ == "__main__":
  if len(sys.argv) >= 3:
    verbose = sys.argv[2] == "-v"
  else:
    verbose = False

  test_names = {}
  for line in sys.stdin:
    test_names[tokenize(line)] = True

  type_1, type_2, correct_names = calculate_errors(sys.argv[1], test_names)

  print "False positives:", len(type_1), "/", (len(type_1) + len(correct_names)), float(len(type_1)) / (len(type_1) + len(correct_names))
  print "False negatives:", len(type_2), "/", (len(type_2) + len(correct_names)), float(len(type_2)) / (len(type_2) + len(correct_names))

  if verbose: 
    for name in type_1:
      print "False positive:", name
    for name in type_2:
      print "False negative:", name
