#!/usr/bin/python
# coding=UTF-8

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

out_file = open("urls.txt", "w")
lock = threading.Lock()

def convert_token(text):
  special_chars = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ".decode("utf-8")
  chars         = "aaaaaaeceeeeiiiidnoooooxouuuuypsaaaaaaeceeeeiiiionooooooouuuuypy"

  new_text = ""
  for c in text:
    index = special_chars.find(c)
    if index != -1:
      new_text += chars[index]
    else:
      new_text += c
  return new_text
     
def tokenize_html(soup):
  tokens = []
  [s.extract() for s in soup('script')]
  [s.extract() for s in soup('style')]
  texts = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
  for text in texts:
    text = convert_token(text.strip()).lower()
    if len(text) == 0 or text == None:
      continue;
 
    tokens = tokens + re.compile("[^a-zA-Z]+").split(text)

  new_tkns = []
  for tkn in tokens:
    if len(tkn) <= 0:
      continue

    if not tkn[0].isupper():
      new_tkns.append(tkn)
  
  return " ".join(new_tkns)

class UrlManager():
  def __init__(self):
    self.urls = []
    self.visited_urls = {}
    self.url_counter = 1

  def push_url(self, url): 
    if len(self.urls) > 1000:
      return False

    if not (url in self.visited_urls):
      if url.count('/') > 4:
        return False
      self.urls = [(self.url_counter, url)] + self.urls
      self.visited_urls[url] = True
      self.url_counter += 1
      random.shuffle(self.urls)
      return True
    else:
      return False

  def pop_url(self): 
    if (len(self.urls) <= 0):
      return ""

    tmp = self.urls[-1]
    del self.urls[-1]
    return tmp

  def has_url(self): 
    return len(self.urls) > 0

  def load_from_file(self, filename):
    with open(filename) as f:
      for url in f:
        self.push_url(url.strip())

  def load_visited_urls(self, filename):
    with open(filename) as f:
      for url in f:
        self.visited_urls[url.strip()] = True

url_manager = UrlManager()

def tokenize_url(url):
  try:
    base_url = url.strip()
    proxy = base_url.replace("http://", "").replace("https://", "")
    proxies = { 'http': proxy }

    r = requests.get(base_url, proxies = { 'http': proxy }, timeout = 5)
    out_file.write(base_url.encode("utf-8") + "\n")
    out_file.flush()

    # Extract links.
    soup = BeautifulSoup(r.text, 'html.parser')
    hrefs = []
    for a in soup.find_all('a'):
      if not a.has_attr('href'):
        continue

      if len(a['href']) <= 0:
        continue

      if a['href'][0] == "#":
        continue

      href = urljoin(base_url, a['href'])
      hrefs.append(href)
    
    counter = 0
    random.shuffle(hrefs) 
    lock.acquire()
    for href in hrefs:
      if url_manager.push_url(href):
        counter += 1
        if counter >= 5:
          break
    lock.release()
      
    print tokenize_html(soup)
    sys.stdout.flush()

  except:
    return

def thread_func():
  while url_manager.has_url():
    lock.acquire()
    url = url_manager.pop_url()[1]
    lock.release()
    tokenize_url(url)

def load_from_file(filename):
  with open(filename) as f:
    for url in f:
      url_manager.push_url(url.strip())

if __name__ == "__main__":
  load_from_file(sys.argv[1])
  url_manager.load_visited_urls("visited_urls.txt")

  while url_manager.has_url():
    tokenize_url(url_manager.pop_url()[1])

  threads = []
  for i in range(0, 4):
    t = threading.Thread(target=thread_func)
    threads.append(t)
    t.start()

  for t in threads:
    t.join()
