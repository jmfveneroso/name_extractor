#!/usr/bin/python
# coding=UTF-8

import os
import sys
import time
import threading
import re
import requests
import datetime
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup
from classifier import Classifier
import heapq

if __name__ == "__main__":
  j = 1175
  with open('non_faculties.txt') as f:
    for url in f:
      url = url.strip()

      if re.match('^http', url) == None:
        url = 'http://' + url

      proxy = url.replace("http://", "").replace("https://", "")
      proxies = { 'http': proxy }
      if len(url) == 0:
        continue

      try:
        r = requests.get(url, proxies = { 'http': proxy }, timeout = 5)
        failed = False
      except requests.exceptions.RequestException as e:
        error = e
        time.sleep(2)
        continue;
      print "Downloaded", url, j

      dir = os.path.dirname(__file__)
      filename = os.path.join(os.path.dirname(__file__), "../name_extractor_data/non_faculty", str(j) + ".html")
      with open(filename, "w") as f:
        f.write(r.text.encode('utf8'))

      j += 1
