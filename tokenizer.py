#!/usr/bin/python
# coding=UTF-8

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
from tokenize_text import convert_token

class Token():
  def __init__(self, tkn, is_first_token, is_name):
    self.tkn = tkn.lower().strip()
    self.is_first_token = is_first_token
    self.is_name = is_name

  def __str__(self):
    return self.tkn + (" 1" if self.is_first_token else " 0") + (" 1" if self.is_name else " 0")

class Tokenizer():
  def __init__(self):
    self.tokens = []
    self.names = []

  def remove_emails(self, text):
    return re.sub('\S+@\S+(\.\S+)+', '', text)
  
  def remove_urls(self, text):
    return re.sub('\S+(\.\S+)+', '', text)

  def tokenize_text(self, text):
    text = self.remove_emails(text)
    text = self.remove_urls(text)
    text = convert_token(text.strip()).lower()
    if len(text) == 0 or text == None:
      return [];
   
    return re.compile("[^a-zA-Z0-9]+").split(text)

  def tokenize_html(self, html):
    soup = BeautifulSoup(html, 'html.parser')
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    texts = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]

    for text in texts:
      text = text.strip()
      if len(text) == 0 or text == None:
        continue;
   
      first_tkn = True
      for name in self.tokenize_text(text):
        if len(name) < 2:
          continue;

        self.tokens.append(Token(name, first_tkn, False))
        first_tkn = False

  def check_sequence(self, pos):
    for name in self.names: 
      match = True
      for i in range(0, len(name)):
        if pos + i >= len(self.tokens) or self.tokens[pos + i].tkn != name[i]:
          match = False
          break
      if match:
        return len(name)  
    return 0

  def mark_names(self):
    i = 0
    while i < len(self.tokens):
      size = self.check_sequence(i)
      if size == 0:
        i += 1
      else:
        for j in range(i, i + size):
          self.tokens[j].is_name = True
        i += size

  def tokenize_file(self, filename):
    with open(filename) as f:
      data = f.read().decode('utf8')
      self.tokenize_html(data)

    self.mark_names()
    for tkn in self.tokens:
      print tkn,

    # i = 0
    # while i < len(self.tokens):
    #   size = self.check_sequence(i)
    #   if size == 0:
    #     print str(self.tokens[i]) + " 0",
    #     i += 1
    #   else:
    #     print " 1 ".join(self.tokens[i:i + size]) + " 1",
    #     i += size
      
    # print " 0 ".join(self.tokens) + " 0"
    self.tokens = []

  def write_tokens(self, filename):
    print " ".join(self.tokens)
    # with open(filename, "w") as f:
    #   data = f.write(" ".join(tokens))

  def load_correct_names(self, filename):
    with open(filename) as f:
      for line in f:
        self.names.append([s.lower() for s in self.tokenize_text(line.decode("utf-8")) if len(s) >= 2])

if __name__ == "__main__":
  start_time = time.time()

  tokenizer = Tokenizer()

  # for i in range(1, 1000):
  #   filename = os.path.join(os.path.dirname(__file__), sys.argv[1], str(i) + ".html")
  #   if os.path.isfile(filename):
  #     tokenizer.tokenize_file(filename)

  tokenizer.load_correct_names(sys.argv[1])
  tokenizer.tokenize_file(sys.argv[2])
  # tokenizer.write_tokens("ibanez")
  # print 'The process took ', time.time() - start_time, 'seconds.'
