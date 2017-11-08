#!/usr/bin/python
# coding=UTF-8

import sys
import random
from urlparse import urlparse
from urlparse import urljoin
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
  filename = sys.argv[1]
  with open(filename) as f:
    for base_url in f:
      base_url = base_url.strip()
      print urlparse(base_url).hostname
