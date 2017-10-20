#!/usr/bin/python
# coding=UTF-8

from math import log
import os
import re
import time
import sys
import random
from urlparse import urlparse
from urlparse import urljoin
import requests
import io
from bs4 import BeautifulSoup
from bs4.element import NavigableString

def is_number(text):
  return re.search('[0-9]', text) != None

class ProbabilityCalculator():
  def __init__(self):
    self.tokens = {}
    self.num_tokens = 0

  def load_file(self, filename):
    with open(filename) as f:
      num_lines = 0
      for line in f:
        tokens = line.split(" ")
        for tkn in tokens:
          tkn = tkn.strip().lower()
          if len(tkn) < 2:
            continue

          if not tkn in self.tokens:
            self.tokens[tkn] = 0
          self.tokens[tkn] += 1
          self.num_tokens += 1
        num_lines += 1
        print num_lines
        sys.stdout.flush()

  def calculate_logs(self):
    counter = 1
    for key in self.tokens:
      self.tokens[key] = (float(self.tokens[key]) + 1) / (self.num_tokens + len(self.tokens.keys()))
      self.tokens[key] = 0 if self.tokens[key] == 0 else log(self.tokens[key])
      counter += 1
      print counter, "in", len(self.tokens)
      sys.stdout.flush()

  def print_probabilities(self):
    self.calculate_logs()
    print "=========="
    for tkn in sorted(self.tokens, key=self.tokens.get, reverse=True):
      print tkn, self.tokens[tkn]
      sys.stdout.flush()

class CondProbabilityCalculator():
  def __init__(self):
    self.tokens = {}
    self.num_tokens = 0
    self.num_names_in_sequence = 0
    self.num_words_in_sequence = 0
    self.words_after = [0] * 7
    self.words_after_words = [0] * 7
    self.names_after = [0] * 7
    self.names_after_words = [0] * 7

  def load_file(self, filename):
    with open(filename) as f:
      for line in f:
        tokens = line.split(" ")
        for i in xrange(0, len(tokens), 2):
          is_name = tokens[i + 1]
          if int(is_name) == 1:
            self.names_after[self.num_names_in_sequence] += 1
            if self.num_words_in_sequence < 6:
              self.names_after_words[self.num_words_in_sequence] += 1
            self.num_names_in_sequence += 1
            self.num_words_in_sequence = 0
          else:
            self.words_after[self.num_names_in_sequence] += 1
            if self.num_words_in_sequence < 6:
              self.words_after_words[self.num_words_in_sequence] += 1
            self.num_names_in_sequence = 0
            self.num_words_in_sequence += 1
      self.names_after[0] = float(self.names_after[0] + 1) / (self.names_after[0] + self.words_after[0] + 2)
      self.names_after[1] = float(self.names_after[1] + 1) / (self.names_after[1] + self.words_after[1] + 2)
      self.names_after[2] = float(self.names_after[2] + 1) / (self.names_after[2] + self.words_after[2] + 2)
      self.names_after[3] = float(self.names_after[3] + 1) / (self.names_after[3] + self.words_after[3] + 2)
      self.names_after[4] = float(self.names_after[4] + 1) / (self.names_after[4] + self.words_after[4] + 2)
      self.names_after[5] = float(self.names_after[5] + 1) / (self.names_after[5] + self.words_after[5] + 2)
      self.words_after_words[0] = float(self.words_after_words[0] + 1) / (self.names_after_words[0] + self.words_after_words[0] + 2)
      self.words_after_words[1] = float(self.words_after_words[1] + 1) / (self.names_after_words[1] + self.words_after_words[1] + 2)
      self.words_after_words[2] = float(self.words_after_words[2] + 1) / (self.names_after_words[2] + self.words_after_words[2] + 2)
      self.words_after_words[3] = float(self.words_after_words[3] + 1) / (self.names_after_words[3] + self.words_after_words[3] + 2)
      self.words_after_words[4] = float(self.words_after_words[4] + 1) / (self.names_after_words[4] + self.words_after_words[4] + 2)
      self.words_after_words[5] = float(self.words_after_words[5] + 1) / (self.names_after_words[5] + self.words_after_words[5] + 2)

  def print_probabilities(self):
    print "0", log(self.names_after[0])
    print "1", log(self.names_after[1]) 
    print "2", log(self.names_after[2])
    print "3", log(self.names_after[3])
    print "4", log(self.names_after[4])
    print "5", log(self.names_after[5])
    print "~0", log(1 - self.names_after[0])
    print "~1", log(1 - self.names_after[1])
    print "~2", log(1 - self.names_after[2])
    print "~3", log(1 - self.names_after[3])
    print "~4", log(1 - self.names_after[4])
    print "~5", log(1 - self.names_after[5])
    print "x0", log(self.words_after_words[0])
    print "x1", log(self.words_after_words[1])
    print "x2", log(self.words_after_words[2])
    print "x3", log(self.words_after_words[3])
    print "x4", log(self.words_after_words[4])
    print "x5", log(self.words_after_words[5])

class FeaturesCalculator():
  def __init__(self):
    self.tokens = {}
    self.is_first_tkn = 0
    self.is_first_tkn_not = 0
    self.street_after = 0
    self.street_after_not = 0
    self.has_hall = 0
    self.has_hall_not = 0
    self.chair_after = 0
    self.chair_after_not = 0
    self.title_before = 0
    self.title_before_not = 0
    self.number_after = 0
    self.number_after_not = 0
    self.less_than_seven_chars = 0
    self.less_than_seven_chars_not = 0
    self.name_count = 0
    self.not_name_count = 0
    self.num_tkns = [0] * 7
    self.num_tkns_not = [0] * 7
    self.elements_with_names = 0
    self.elements_with_no_names = 0

  def load_file(self, filename):
    all_tokens = []
    with open(filename) as f:
      for line in f:
        current_name = []
        tokens = line.split(" ")
        all_tokens = all_tokens + line.split(" ")
        el_token_count = 0
        found_name = False
        for i in xrange(0, len(tokens), 3):
          is_first_tkn = tokens[i + 1] == "1"
          is_name = tokens[i + 2] == "1"

          if is_first_tkn:
            el_token_count = el_token_count if el_token_count < 5 else 5
            if found_name:
              self.num_tkns[el_token_count] += 1
              self.elements_with_names += 1
            else:
              self.num_tkns_not[el_token_count] += 1
              self.elements_with_no_names += 1
            el_token_count = 0
            found_name = False
          el_token_count += 1

          if int(is_name) == 1:
            found_name = True
            if len(current_name) == 0: # Start of name.
              self.name_count += 1
              if is_first_tkn:
                self.is_first_tkn += 1

              if i - 3 > 0 and tokens[i - 3] in ["mr", "mrs", "dr", "ms"]:
                self.title_before += 1

              if i - 3 > 0 and is_number(tokens[i - 3]) and not is_first_tkn:
                print tokens[i - 3], tokens[i]
                self.number_after += 1

            current_name.append(tokens[i])
          else:
            if len(current_name) > 0: # End of name.
              if current_name[-1] == "hall":
                self.has_hall += 1

              if tokens[i] in ["st", "street", "ave", "avenue", "highway"] and not is_first_tkn:
                self.street_after += 1

              if is_number(tokens[i]):
                self.number_after += 1

              # if tokens[i] == "chair" or tokens[i] == "lectureship":
              #   self.chair_after += 1
              if len("".join(current_name)) < 7:
                self.less_than_seven_chars += 1

            else: # Last word was not a name.
              if tokens[i] in ["st", "street", "ave", "avenue", "highway"]:
                self.street_after_not += 2

              if is_number(tokens[i]):
                self.number_after_not += 2
              # if tokens[i] == "chair" or tokens[i] == "lectureship":
              #   self.chair_after_not += 1

              if i - 3 > 0 and tokens[i - 3] in ["mr", "mrs", "dr"]:
                self.title_before_not += 2

            current_name = []
            if tokens[i] == "hall":
              self.has_hall_not += 2

            if is_first_tkn:
              self.is_first_tkn_not += 2
            self.not_name_count += 1


    words = []
    for i in xrange(0, len(all_tokens), 3):
      is_name = all_tokens[i + 2] == "1"

      if not int(is_name) == 1:
        words.append(all_tokens[i])
   
    for i in xrange(0, len(words), 2):
      if len("".join(words[i:i+1])) < 7:
        self.less_than_seven_chars_not += 1
      if len("".join(words[i:i+2])) < 7:
        self.less_than_seven_chars_not += 1

    # self.not_name_count /= 2

  def print_probabilities(self):
    print "is_first_tkn",     (float(self.is_first_tkn + 1) / (self.name_count + 2)        )
    print "is_first_tkn_not", (float(self.is_first_tkn_not + 1) / (self.not_name_count + 2))
    print "street_after",     (float(self.street_after + 1) / (self.name_count + 2)        )
    print "street_after_not", (float(self.street_after_not + 1) / (self.not_name_count + 2))
    print "has_hall",         (float(self.has_hall + 1) / (self.name_count + 2)            )
    print "has_hall_not",     (float(self.has_hall_not + 1) / (self.not_name_count + 2)    )
    print "title_before",     (float(self.title_before + 1) / (self.name_count + 2)        )
    print "title_before_not", (float(self.title_before_not + 1) / (self.not_name_count + 2))
    print "number_after",     (float(self.number_after + 1) / (self.name_count + 2)        )
    print "number_after_not", (float(self.number_after_not + 1) / (self.not_name_count + 2))
    print "less_than_seven_chars", (float(self.less_than_seven_chars + 1) / (self.name_count + 2)        )
    print "less_than_seven_chars_not", (float(self.less_than_seven_chars_not + 1) / (self.not_name_count + 2))
    print "num_tkns_0", (float(self.num_tkns[0] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_0", (float(self.num_tkns_not[0] + 1) / (self.not_name_count + self.elements_with_no_names))
    print "num_tkns_1", (float(self.num_tkns[1] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_1", (float(self.num_tkns_not[1] + 1) / (self.not_name_count + self.elements_with_no_names))
    print "num_tkns_2", (float(self.num_tkns[2] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_2", (float(self.num_tkns_not[2] + 1) / (self.not_name_count + self.elements_with_no_names))
    print "num_tkns_3", (float(self.num_tkns[3] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_3", (float(self.num_tkns_not[3] + 1) / (self.not_name_count + self.elements_with_no_names))
    print "num_tkns_4", (float(self.num_tkns[4] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_4", (float(self.num_tkns_not[4] + 1) / (self.not_name_count + self.elements_with_no_names))
    print "num_tkns_5", (float(self.num_tkns[5] + 1) / (self.name_count + self.elements_with_names))
    print "num_tkns_not_5", (float(self.num_tkns_not[5] + 1) / (self.not_name_count + self.elements_with_no_names))
    # print "num_tkns_6", (float(self.num_tkns[6] + 1) / (self.name_count + self.elements_with_names))
    # print "num_tkns_not_6", (float(self.num_tkns_not[6] + 1) / (self.not_name_count + self.elements_with_no_names))
    # print "is_first_tkn", self.is_first_tkn, self.name_count
    # print "is_first_tkn_not", self.is_first_tkn_not, self.not_name_count
    # print "street_after", self.street_after, self.name_count
    # print "street_after_not", self.street_after_not, self.not_name_count
    # print "has_hall", self.has_hall, self.name_count
    # print "has_hall_not", self.has_hall_not, self.not_name_count
    # print "chair_after", self.chair_after, self.name_count
    # print "chair_after_not", self.chair_after_not, self.not_name_count
    # print "title_before", self.title_before, self.name_count
    # print "title_before_not", self.title_before_not, self.not_name_count
    # print "number_after", self.number_after, self.name_count
    # print "number_after_not", self.number_after_not, self.not_name_count
    # print "less_than_seven_chars", self.less_than_seven_chars, self.name_count
    # print "less_than_seven_chars_not", self.less_than_seven_chars_not, self.not_name_count


if __name__ == "__main__":
  if sys.argv[1] == "general":
    probability_calc = ProbabilityCalculator()
    probability_calc.load_file(sys.argv[2])
    probability_calc.print_probabilities()
  elif sys.argv[1] == "cond":
    probability_calc = CondProbabilityCalculator()
    probability_calc.load_file(sys.argv[2])
    probability_calc.print_probabilities()
  elif sys.argv[1] == "features":
    probability_calc = FeaturesCalculator()
    probability_calc.load_file(sys.argv[2])
    probability_calc.print_probabilities()
