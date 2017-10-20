#!/usr/bin/python
# coding=UTF-8

from math import log
import re
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
import sys
import random
from urlparse import urlparse
from urlparse import urljoin
import requests
import io
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from tokenize_text import convert_token

verbose = False

def compare(x, y):
  return int((float(y[0]) - float(y[1])) - (float(x[0]) - float(x[1])))

def compare_tuples(t1, t2):
  return int((float(t2[0]) - float(t1[0])))

def remove_emails(text):
  return re.sub('\S+@\S+(\.\S+)+', '', text)

def remove_urls(text):
  regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
  return re.sub(regex, '', text)

def remove_titles(text):
  text = re.sub('(M\. Sc\.)|(M\.Sc\.)', '', text)
  text = re.sub('(Ph\. D\.)|(Ph\.D\.)', '', text)
  text = re.sub('(M\. S\.)|(M\.S\.)', '', text)
  return re.sub('M\.Sc\.', '', text)

def is_number(text):
  return re.search('[0-9]', text) != None

def tokenize_text(text):
  text = remove_emails(text)
  text = remove_urls(text)
  text = remove_titles(text)
  text = convert_token(text.strip()).lower()
  if len(text) == 0 or text == None:
    return [];
 
  return re.compile("[^a-zA-Z0-9]+").split(text)

def tokenize_html(soup):
  tokens = []
  [s.extract() for s in soup('script')]
  [s.extract() for s in soup('style')]
  texts = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
  for text in texts:
    tokens = tokens + tokenize_text(text)

  new_tkns = []
  for tkn in tokens:
    if len(tkn) > 0:
      new_tkns.append(tkn)
  
  return " ".join(new_tkns)

class Model():
  def __init__(self):
    self.name_cond_probs = {}
    self.word_cond_probs = {}
    self.name_probs = [None] * 6
    self.word_probs = [None] * 6
    self.word_after_name_probs = [None] * 6
    self.name_cond_count = 0
    self.word_cond_count = 0
    self.name_count = 0
    self.found_names = {}
    self.repeating_names = {}
    self.not_name_count = 0
    self.name_count = 0
    self.uncertain = {}

    self.is_first_tkn     = 0
    self.is_first_tkn_not = 0
    self.street_after     = 0
    self.street_after_not = 0
    self.has_hall         = 0
    self.has_hall_not     = 0
    self.title_before     = 0
    self.title_before_not = 0
    self.number_after     = 0
    self.number_after_not = 0
    self.less_than_seven_chars = 0
    self.less_than_seven_chars_not = 0
    self.num_tkns       = [0] * 6
    self.num_tkns_not   = [0] * 6

    self.first_parents = {}
    self.second_parents = {}
    self.class_names = {}
    self.second_class_names = {}
    self.first_tkn_pos = {}
    self.child_pos_ = {}
    self.words_in_field = {}
    self.first_parents_ = {}
    self.second_parents_ = {}
    self.class_names_ = {}
    self.second_class_names_ = {}
    self.first_tkn_pos_ = {}
    self.child_pos__ = {}
    self.words_in_field_ = {}

  def splitnonalpha(self, s):
    return re.compile("[ `\-=~!#$%^&*()_+\[\]{};\'\\:\"|<,/<>?]+").split(s)
 
  def prob_name(self, tkns):
    prob_true = 0
    for i in range(0, len(tkns)):
      # if not re.compile("^([a-zA-Z]+\.?)+$").match(tkns[i]) != None: 
      #   return -1000

      cond_prob = log(float(1) / (3831851 + len(self.name_cond_probs)))
      tkn = tkns[i].strip().lower()
      if tkn in self.name_cond_probs:
        cond_prob = self.name_cond_probs[tkn]
      # else:
      #   print tkn.encode("utf-8"), "name not found"
 
      # print "prob name self", self.name_probs[i]
      # print "prob name", tkns[i].encode("utf-8"), cond_prob
      # print "=========="
      prob_true += self.name_probs[i] + cond_prob
    return prob_true

  def prob_word(self, tkns):
    prob_true = 0
    for i in range(0, len(tkns)):
      cond_prob = log(float(1) / (84599521 + len(self.word_cond_probs)))
      tkn = tkns[i].strip().lower()
      if tkn in self.word_cond_probs:
        cond_prob = self.word_cond_probs[tkn]
      # else:
      #   print tkn.encode("utf-8"), "word not found"
 
      # print "prob word self", self.word_probs[i]
      # print "prob word", tkns[i].encode("utf-8"), cond_prob
      prob_true += self.word_probs[i] + cond_prob
    return prob_true

  def tkns_are_name(self, tkns, is_first_tkn, last_word, next_word, use_extra_features, extra_features, first_tkn_pos):
    if len([t for t in tkns if re.search('[0-9]', t) != None]) > 0:
      return [0, 1]
    if len([t for t in tkns if t in ["mr", "mrs", "ms", "dr", "professor", "miss"]]) > 0:
      return [0, 1]

    street_after = next_word in ["st", "street", "ave", "avenue", "highway"]
    has_hall = "hall" in tkns or next_word == "hall"
    title_before = last_word in ["mr", "mrs", "dr", "ms"]
    number_after = is_number(next_word) or is_number(last_word)
    less_than_seven_chars = len("".join(tkns)) < 7

    num_tkns = extra_features['words_in_field']
    num_tkns = num_tkns if num_tkns < 5 else 5

    # Is name.
    prob_name = self.prob_name(tkns)
    # prob_name += log(self.number_after) if number_after else log(1 - self.number_after)
    # prob_name += log(self.is_first_tkn) if is_first_tkn else log(1 - self.is_first_tkn)
    prob_name += log(self.street_after) if street_after else log(1 - self.street_after)
    prob_name += log(self.has_hall) if has_hall else log(1 - self.has_hall)
    prob_name += log(self.less_than_seven_chars) if less_than_seven_chars else log(1 - self.less_than_seven_chars)
    prob_name += log(self.title_before) if title_before else log(1 - self.title_before)
    prob_name += log(self.num_tkns[num_tkns])

    # Is not a name.
    prob_word = self.prob_word(tkns)
    # prob_word += log(self.number_after_not) if number_after else log(1 - self.number_after_not)
    # prob_word += log(self.is_first_tkn_not) if is_first_tkn else log(1 - self.is_first_tkn_not)
    prob_word += log(self.street_after_not) if street_after else log(1 - self.street_after_not)
    prob_word += log(self.has_hall_not) if has_hall else log(1 - self.has_hall_not)
    prob_word += log(self.less_than_seven_chars_not) if less_than_seven_chars else log(1 - self.less_than_seven_chars_not)
    prob_word += log(self.title_before_not) if title_before else log(1 - self.title_before_not)
    prob_word += log(self.num_tkns_not[num_tkns])


    if use_extra_features:
      prob_name += self.first_parents_[extra_features['first_parent']][0]
      prob_word += self.first_parents_[extra_features['first_parent']][1]
      prob_name += self.second_parents_[extra_features['second_parent']][0]
      prob_word += self.second_parents_[extra_features['second_parent']][1]
      prob_name += self.class_names_[extra_features['class_name']][0]
      prob_word += self.class_names_[extra_features['class_name']][1]
      # prob_name += self.second_class_names_[extra_features['second_class_name']][0]
      # prob_word += self.second_class_names_[extra_features['second_class_name']][1]
      prob_name += self.child_pos__[extra_features['child_pos']][0]
      prob_word += self.child_pos__[extra_features['child_pos']][1]
      # prob_name += self.first_tkn_pos_[first_tkn_pos][0]
      # prob_word += self.first_tkn_pos_[first_tkn_pos][1]
      # prob_name += self.words_in_field_[extra_features['words_in_field']][0]
      # prob_word += self.words_in_field_[extra_features['words_in_field']][1]
      # print tkns, extra_features['words_in_field'], self.words_in_field_[extra_features['words_in_field']][0], self.words_in_field_[extra_features['words_in_field']][1]
      # print tkns, self.words_in_field_

    if verbose:
      print tkns, float(prob_name), float(prob_word)
    return [float(prob_name), float(prob_word)]

  def tkn_probs(self, tkns):
    return self.prob_name(tkns), self.prob_word(tkns)

  def extract_names(self, html, calculate_probs):
    self.found_names = {}
    self.repeating_names = {}
    self.first_parents = {}
    self.second_parents = {}
    self.class_names = {}
    self.second_class_names = {}
    self.child_pos_ = {}
    self.first_tkn_pos = {}
    self.words_in_field = {}
    self.name_count = 0
    self.not_name_count = 0

    soup = BeautifulSoup(html, 'html.parser')
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]

    elements = {}
  
    texts = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
    for text in texts:
      old_text = text
      text = text.strip()
      if len(text) == 0 or text == None:
        continue;

      current_name = []
      # tkns = self.splitnonalpha(text)
      tkns = tokenize_text(text)
      tkns = [t for t in tkns if (len(t) > 0 and re.match("^\S+$", t) != None)]

      extra_features = {}
      first_parent = old_text.parent
      second_parent = old_text.parent.parent

      class_name = " ".join(old_text.parent.get("class") if old_text.parent.has_attr("class") else [])
      second_class_name = " ".join(old_text.parent.parent.get("class") if old_text.parent.parent.has_attr("class") else [])

      children = first_parent.children
      words_in_field = len(tkns)
  
      child_pos = 0
      child = old_text
      while child != None:
        child = child.parent
        child_pos += 1

      first_parent_name = first_parent.name + second_parent.name
      if not first_parent_name  in self.first_parents:      self.first_parents[first_parent_name] = [0, 0]
      if not second_parent.name in self.second_parents:     self.second_parents[second_parent.name] = [0, 0]
      if not class_name         in self.class_names:        self.class_names[class_name] = [0, 0]
      if not second_class_name  in self.second_class_names: self.second_class_names[second_class_name] = [0, 0]
      if not child_pos          in self.child_pos_:         self.child_pos_[child_pos] = [0, 0]
      if not words_in_field     in self.words_in_field:     self.words_in_field[words_in_field] = [0, 0]
      extra_features['first_parent'] = first_parent_name
      extra_features['second_parent'] = second_parent.name
      extra_features['class_name'] = class_name
      extra_features['second_class_name'] = second_class_name
      extra_features['child_pos'] = child_pos
      extra_features['words_in_field'] = words_in_field

      name_found = False
      first_tkn = True
      i = 0 
      while i < len(tkns):
        current_name = []
        name_length = 0
        old_i = i

        last_word = tkns[i - 1] if (i - 1 >= 0) else ""

        tkn_probs = [None] * 5
        if i <= len(tkns) - 4:
          tkn_probs[4] = self.tkns_are_name(tkns[i:i + 4], first_tkn, last_word, tkns[i + 4] if i + 4 < len(tkns) else "", not calculate_probs, extra_features, old_i)
          if not " ".join(tkns[i:i + 4]) in self.repeating_names:
            self.repeating_names[" ".join(tkns[i:i + 4])] = 0
          self.repeating_names[" ".join(tkns[i:i + 4])] += 1

        if i <= len(tkns) - 3: 
          tkn_probs[3] = self.tkns_are_name(tkns[i:i + 3], first_tkn, last_word, tkns[i + 3] if i + 3 < len(tkns) else "", not calculate_probs, extra_features, old_i)
          if not " ".join(tkns[i:i + 3]) in self.repeating_names:
            self.repeating_names[" ".join(tkns[i:i + 3])] = 0
          self.repeating_names[" ".join(tkns[i:i + 3])] += 1

        if i <= len(tkns) - 2: 
          tkn_probs[2] = self.tkns_are_name(tkns[i:i + 2], first_tkn, last_word, tkns[i + 2] if i + 2 < len(tkns) else "", not calculate_probs, extra_features, old_i)
          if not " ".join(tkns[i:i + 2]) in self.repeating_names:
            self.repeating_names[" ".join(tkns[i:i + 2])] = 0
          self.repeating_names[" ".join(tkns[i:i + 2])] += 1

        if tkn_probs[4] != None and tkn_probs[4][0] > tkn_probs[4][1]:
          name_length = 4
          i += 4
        elif tkn_probs[3] != None and tkn_probs[3][0] > tkn_probs[3][1]:
          name_length = 3
          i += 3
        elif tkn_probs[2] != None and tkn_probs[2][0] > tkn_probs[2][1]:
          name_length = 2
          i += 2
        else:
          name_length = 0
          # print tkns[i:i + 4], "not name", self.tkn_probs(tkns[i:i + 4]), self.tkn_probs(tkns[i:i + 3]), self.tkn_probs(tkns[i:i + 2])
          i += 1

        if name_length > 0:
          name_found = True
          name_tkns = tkns[old_i:old_i+name_length]
          if len([t for t in name_tkns if len(t) > 1]) == 0:
            continue

          if len(name_tkns) <= 1:
            continue
        
          # ponderation = float(tkn_probs[name_length][1] - tkn_probs[name_length][0]) / (tkn_probs[name_length][0] + tkn_probs[name_length][1])
          ponderation = 1

          name = " ".join(name_tkns)
          name = re.sub('(ed d$)|(ph$)|(ph d$)|(m s$)', '', name).encode('utf-8')
          if not name in self.found_names:
            self.name_count += ponderation
            if calculate_probs:
              self.first_parents[first_parent_name][0] += ponderation
              self.second_parents[second_parent.name][0] += ponderation
              self.class_names[class_name][0] += ponderation
              self.second_class_names[second_class_name][0] += ponderation
              self.child_pos_[child_pos][0] += ponderation
              self.words_in_field[words_in_field][0] += ponderation
              if not old_i in self.first_tkn_pos: self.first_tkn_pos[old_i] = [0, 0]
              self.first_tkn_pos[old_i][0] += ponderation

          self.found_names[name] = tkn_probs[name_length]

        if not name_found:
          self.not_name_count += 1
          if calculate_probs:
            self.first_parents[first_parent_name][1] += 1
            self.second_parents[second_parent.name][1] += 1
            self.class_names[class_name][1] += 1
            self.second_class_names[second_class_name][1] += 1
            self.child_pos_[child_pos][1] += 1
            self.words_in_field[words_in_field][1] += 1
            if not old_i in self.first_tkn_pos: self.first_tkn_pos[old_i] = [0, 0]
            self.first_tkn_pos[old_i][1] += 1

      first_tkn = False

    if not calculate_probs:
      for name in sorted(self.found_names, cmp=compare, key=self.found_names.get):
        # if self.repeating_names[name] == 1: # Gambiarra. mehlor calcular probs.
        if verbose: print name, self.found_names[name]
        else: print name

      # print self.first_parents_
      # print self.second_parents
      # print self.class_names
      # print self.child_pos_
      # print self.words_in_field_

  def calculate_probs(self):
    for key in self.first_parents:
      self.first_parents_[key] = [0, 0]
      self.first_parents_[key][0] = log(float(self.first_parents[key][0] + 1) / (self.name_count + len(self.first_parents)))
      self.first_parents_[key][1] = log(float(self.first_parents[key][1] + 1) / (self.not_name_count + len(self.first_parents)))
      # print "first", key, self.first_parents[key][0], self.first_parents[key][1]
    for key in self.second_parents:
      self.second_parents_[key] = [0, 0]
      # self.second_parents_[key][0] = log(float(self.second_parents[key][0] + 1) / (self.name_count + len(self.second_parents)))
      # self.second_parents_[key][1] = log(float(self.second_parents[key][1] + 1) / (self.not_name_count + len(self.second_parents)))
      # print "second", key, self.second_parents[key][0], self.second_parents[key][1]
    for key in self.class_names:
      self.class_names_[key] = [0, 0]
      self.class_names_[key][0] = log(float(self.class_names[key][0] + 1) / (self.name_count + len(self.class_names)))
      self.class_names_[key][1] = log(float(self.class_names[key][1] + 1) / (self.not_name_count + len(self.class_names)))
    for key in self.second_class_names:
      self.second_class_names_[key] = [0, 0]
      self.second_class_names_[key][0] = log(float(self.second_class_names[key][0] + 1) / (self.name_count + len(self.second_class_names)))
      self.second_class_names_[key][1] = log(float(self.second_class_names[key][1] + 1) / (self.not_name_count + len(self.second_class_names)))
      # print "class_names", key, self.class_names[key][0], self.class_names[key][1]
    for key in self.child_pos_:
      self.child_pos__[key] = [0, 0]
      self.child_pos__[key][0] = log(float(self.child_pos_[key][0] + 1) / (self.name_count + len(self.child_pos_)))
      self.child_pos__[key][1] = log(float(self.child_pos_[key][1] + 1) / (self.not_name_count + len(self.child_pos_)))
      # print "child_pos", key, self.child_pos_[key][0], self.child_pos_[key][1]
    for key in self.first_tkn_pos:
      self.first_tkn_pos_[key] = [0, 0]
      self.first_tkn_pos_[key][0] = log(float(self.first_tkn_pos[key][0] + 1) / (self.name_count + len(self.first_tkn_pos)))
      self.first_tkn_pos_[key][1] = log(float(self.first_tkn_pos[key][1] + 1) / (self.not_name_count + len(self.first_tkn_pos)))
    for key in self.words_in_field:
      self.words_in_field_[key] = [0, 0]
      self.words_in_field_[key][0] = log(float(self.words_in_field[key][0] + 1) / (self.name_count + len(self.words_in_field)))
      self.words_in_field_[key][1] = log(float(self.words_in_field[key][1] + 1) / (self.not_name_count + len(self.words_in_field)))

    # print sorted(self.first_parents_, cmp=compare_tuples, key=self.first_parents_.get)[0]
    # for key in sorted(self.first_parents_, cmp=compare_tuples, key=self.first_parents_.get)[1:]:
    #   self.first_parents_[key][0] = -5
    #   self.first_parents_[key][1] = 0
    # for key in sorted(self.second_parents, cmp=compare, key=self.second_parents.get)[1:]:
    #   self.second_parents[key][0] = -10
    #   self.second_parents[key][1] = 0
    # for key in sorted(self.class_names, cmp=compare, key=self.class_names.get)[1:]:
    #   self.class_names[key][0] = -10
    #   self.class_names[key][1] = 0
    # for key in sorted(self.child_pos_, cmp=compare, key=self.child_pos_.get)[1:]:
    #   self.child_pos_[key][0] = -10
    #   self.child_pos_[key][1] = 0

  def load_name_cond_probs(self, filename):
    with open(filename) as f:
      for line in f:
        word, prob = line.split(" ")
        self.name_cond_probs[word] = float(prob.strip())

  def load_word_cond_probs(self, filename):
    with open(filename) as f:
      for line in f:
        word, prob = line.split(" ")
        self.word_cond_probs[word] = float(prob.strip())

  def load_name_probs(self, filename):
    with open(filename) as f:
      for i in range(0, 6):
        line = f.readline().split(" ")[1]
        self.name_probs[i] = float(line)

      for i in range(0, 6):
        line = f.readline().split(" ")[1]
        self.word_after_name_probs[i] = float(line)

      for i in range(0, 6):
        line = f.readline().split(" ")[1]
        self.word_probs[i] = float(line)

  def load_feature_probs(self, filename):
    with open(filename) as f:
      self.is_first_tkn     = float(f.readline().split(" ")[1])
      self.is_first_tkn_not = float(f.readline().split(" ")[1])
      self.street_after     = float(f.readline().split(" ")[1])
      self.street_after_not = float(f.readline().split(" ")[1])
      self.has_hall         = float(f.readline().split(" ")[1])
      self.has_hall_not     = float(f.readline().split(" ")[1])
      self.title_before     = float(f.readline().split(" ")[1])
      self.title_before_not = float(f.readline().split(" ")[1])
      self.number_after     = float(f.readline().split(" ")[1])
      self.number_after_not = float(f.readline().split(" ")[1])
      self.less_than_seven_chars = float(f.readline().split(" ")[1])
      self.less_than_seven_chars_not = float(f.readline().split(" ")[1])
      for i in range(0, 6):
        self.num_tkns[i] = float(f.readline().split(" ")[1])
        self.num_tkns_not[i] = float(f.readline().split(" ")[1])

  def print_name_cond_probs(self):
    for tkn in sorted(self.name_cond_probs, key=self.name_cond_probs.get, reverse=True):
      print "%s %.8f" % (tkn, float(self.name_cond_probs[tkn]))

  def print_word_cond_probs(self):
    for tkn in sorted(self.word_cond_probs, key=self.word_cond_probs.get, reverse=True):
      print "%s %.8f" % (tkn, float(self.word_cond_probs[tkn]))

  def print_name_probs(self):
    for i in range(0, 5):
      print "name %d %.4f" % (i, float(self.name_probs[i]))
      print "word %d %.4f" % (i, float(self.word_probs[i]))

if __name__ == "__main__":
  model = Model()
  model.load_name_cond_probs("data/probabilities/tokenized_authors_prob.txt")
  model.load_word_cond_probs("data/probabilities/conditional_not_a_name_prob.txt")
  model.load_name_probs("data/probabilities/name_log_prob_3.txt")
  model.load_feature_probs("data/probabilities/feature_probs.txt")
  # model.print_name_probs()
  # model.print_name_cond_probs()
  # model.print_word_cond_probs()

  if len(sys.argv) > 2 and sys.argv[2] == '-v':
    verbose = True
  
  with open(sys.argv[1]) as f:
    html =  f.read()
    model.extract_names(html, True)
    model.calculate_probs()
    model.extract_names(html, False)
