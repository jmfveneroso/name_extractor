#!/usr/bin/python
# coding=UTF-8

import re
import os
import io
import sys
import time
from bs4 import BeautifulSoup
from bs4.element import NavigableString

def convert_token(text):
  special_chars = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿš".decode("utf-8")
  chars         = "aaaaaaeceeeeiiiidnoooooxouuuuypsaaaaaaeceeeeiiiionooooooouuuuypys"

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
 
  return re.compile("[^a-zA-Z0-9]+").split(text)

def tokenize(html):
  soup = BeautifulSoup(html, 'html.parser')
  [s.extract() for s in soup('script')]
  [s.extract() for s in soup('style')]

  texts = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
  tkns = []
  for text in texts:
    tkns = tkns + tokenize_text(text)

  tkns = [t for t in tkns if (len(t) > 0 and re.match("^\S+$", t) != None)]
  print " ".join(tkns)

if __name__ == "__main__":
  with io.open(sys.argv[1], encoding='utf-8') as f:
    html =  f.read()
    tokenize(html)
