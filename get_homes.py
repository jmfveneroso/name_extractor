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
      proxy = base_url.replace("http://", "").replace("https://", "")
      proxies = { 'http': proxy }

      r = None
      try:
        r = requests.get(base_url, proxies = { 'http': proxy }, timeout = 5)
      except:
        continue;

      soup = BeautifulSoup(r.text, 'html.parser')
 
      links = []
      for a in soup.find_all('a'):
        if a.has_attr('href'):
          if len(a['href']) > 0 and a['href'][0] == "#":
            continue
        else:
          continue

        href = urljoin(base_url, a['href'])
        if urlparse(base_url).hostname == urlparse(href).hostname:
          if len(urlparse(href).path) > 0 and href != base_url:
            links.append(urlparse(href).geturl())
        
      links = list(set(links))
      random.shuffle(links)         
      for l in links[:5]:
        print l
