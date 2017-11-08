#!/usr/bin/python
# coding=UTF-8

import io
import os
import re
import sys
import time
import threading
import requests
import random
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup
from bs4.element import NavigableString

def convert_token(text):
  special_chars = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿšŽčžŠšČłńężść".decode("utf-8")
  chars         = "aaaaaaeceeeeiiiidnoooooxouuuuypsaaaaaaeceeeeiiiionooooooouuuuypysZczSsClnezsc"

  new_text = ""
  for c in text:
    index = special_chars.find(c)
    if index != -1:
      new_text += chars[index]
    else:
      new_text += c
  return new_text

def tokenize_text(text):
  text = convert_token(text.strip()).lower()
  if len(text) == 0 or text == None:
    return [];
 
  return re.compile("[^a-zA-Z]+").split(text)

if __name__ == "__main__":
  count = 0
  line_count = 0
  with io.open(sys.argv[1], encoding='utf-8') as f:
    for line in f:
      # tokens = tokenize_text(line)
      count += len(line.split(" ")) + 1
      line_count += 1
      print line_count, count
      # print " ".join(tokens)
  print count
