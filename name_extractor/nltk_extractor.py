# coding=UTF-8

import os
import re
from math import log
import nltk
import sys
import tokenizer
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from bs4.element import NavigableString

class NltkExtractor():
  def ie_preprocess(self, document):
    stop = stopwords.words('english')
    document = ' '.join([i for i in document.split() if i not in stop])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences
  
  def extract_names(self, document):
    names = []
    sentences = self.ie_preprocess(document)
    for tagged_sentence in sentences:
      for chunk in nltk.ne_chunk(tagged_sentence):
        if type(chunk) == nltk.tree.Tree:
          if chunk.label() == 'PERSON':
            names.append(' '.join([c[0] for c in chunk]))
  
    t = tokenizer.Tokenizer()
    names2 = []
    for name in names:
      name = " ".join(t.tokenize_text(name.strip()))
      if not name in names2:
        names2.append(name.strip())
    return names2

  def fit(self, docs):
    pass

  def extract(self, html):
    soup = BeautifulSoup(html, 'html.parser')

    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    for br in soup.find_all("br"):
      if len(br.findChildren()) == 0:
        br.replace_with(" ")

    document = ''
    n_strs = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
    for n_str in n_strs:
      content = n_str.strip()
      if len(content) == 0 or content is None:
        continue;

      # Tokenize content and remove double spaces.
      document += content
      document += '\n'

    names = self.extract_names(document)
    # for n in names:
    #   print n
    return names
