#!/usr/bin/python
# coding=UTF-8

import sys
import io
import os
import re
from tokenize_text import tokenize_text

names = {}
actual_names = {}

def tokenize(text):
  return (" ".join(tokenize_text(text.decode("utf-8").strip()))).strip()

with open(sys.argv[1]) as f:
  for line in f:
    names[tokenize(line)] = True

if len(sys.argv) >= 3:
  verbose = sys.argv[2] == "-v"
else:
  verbose = False

false_positive_count = 0
false_negative_count = 0

if not os.isatty(0):
  for line in sys.stdin:
    actual_names[tokenize(line)] = True
    if not tokenize(line) in names:
      if verbose: print "False positive", tokenize(line)
      false_positive_count += 1
  
else:
  with io.open(sys.argv[2], encoding="utf-8") as f:
    for line in f:
      actual_names[tokenize(line)] = True
      if not tokenize(line) in names:
        if verbose: print "False positive", tokenize(line)
        false_positive_count += 1
  
for n in names:
  if not tokenize(n) in actual_names:
    if verbose: print "False negative", tokenize(n)
    false_negative_count += 1

print "False positives:", false_positive_count, "/", len(actual_names), float(false_positive_count) / len(actual_names)
print "False negatives:", false_negative_count, "/", len(names), float(false_negative_count) / len(names)
