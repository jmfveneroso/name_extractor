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
import warc
import signal
import orm
import find_dblp_researcher

def now(): 
  return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())

def bla():
  x = datetime.datetime.utcnow()
  y = datetime.datetime.utcnow() + datetime.timedelta(0,3)
  return str(datetime.datetime.utcnow())[:-7]

# Uncrawled URL.
class Url():
  def __init__(self, url, timestamp):
    self.url = url
    self.timestamp = timestamp
  
  def __cmp__(self, other):
    if now() <= self.timestamp:
      return True
    elif now() <= other.timestamp:
      return False
    return len(self.url) > len(other.url)

  def __str__(self):
    return self.url

# Scheduler.
class UrlManager():
  def __init__(self):
    self.urls = []
    self.visited_urls = {}
    self.downloaded_urls = {}

  def push_url(self, url): 
    try:
      url.decode('ascii')
    except UnicodeEncodeError, UnicodeDecodeError:
      return

    if not (url in self.visited_urls):
      heapq.heappush(self.urls, Url(url, now()))
      self.visited_urls[url] = 0

  def enforce_politeness_policy(self, obj): 
    base_url = urlparse(obj.url).hostname
    if base_url == None:
      return False

    if not base_url in self.visited_urls: 
      self.visited_urls[base_url] = now() + 3
      return False
    elif now() >= self.visited_urls[base_url]:
      self.visited_urls[base_url] = now() + 3
      return False
    return True
    
  def pop_url(self): 
    if (len(self.urls) == 0):
      return ""

    obj = heapq.heappop(self.urls)
    if self.enforce_politeness_policy(obj):
      heapq.heappush(self.urls, Url(obj.url, now() + 5))
      return ""

    return obj.url

  def has_url(self): 
    return len(self.urls) > 0

  def load_visited_urls(self, filename):
    if not os.path.isfile(filename):
      return

    f = open(filename, "r")
    for url in f:
      self.visited_urls[url] = now() - 10
    f.close()

  def load_unvisited_urls(self, filename):
    if not os.path.isfile(filename):
      return

    f = open(filename, "r")
    for url in f:
      self.push_url(url.strip())
    f.close()

  def save_visited_urls(self, filename):
    f = open(filename, "w")
    for url in self.downloaded_urls:
      f.write(url + "\n")

  def save_unvisited_urls(self, filename):
    f = open(filename, "w")
    for url in self.urls:
      f.write(url.url + "\n")

class UniTrackerThread(threading.Thread):
  lock = threading.Lock()

  def __init__(self, url_manager, output_dir, thread_id, warc_file):
    threading.Thread.__init__(self)
    self.url_manager = url_manager
    self.thread_id = thread_id
    self.output_dir = output_dir
    self.classifier = Classifier()

  def get_clean_url(self, url): 
    if url == None: return ''
    url = re.sub('(^http\:\/\/)|(^https\:\/\/)', '', url)
    return re.sub('^www\.', '', url)

  def get_main_domain(self, url): 
    top_level_domains = [
      'com', 'edu', 'gov', 'org', 'net', 'int', 'mil', 'ac', 'ad', 'ae', 
      'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'as', 'at', 
      'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 
      'bi', 'bj', 'bl', 'bm', 'bn', 'bo', 'bq', 'br', 'bs', 'bt', 'bv', 
      'bw', 'by', 'bz', 'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 
      'cl', 'cm', 'cn', 'co', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 
      'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 
      'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 
      'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp', 'gq', 
      'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 
      'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir', 'is', 'it', 
      'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 
      'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 
      'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 
      'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 
      'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nc', 'ne', 'nf', 'ng', 'ni', 
      'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'pa', 'pe', 'pf', 'pg', 
      'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 
      're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 
      'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss', 'st', 
      'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 
      'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'tt', 'tv', 'tw', 'tz', 
      'ua', 'ug', 'uk', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 
      'vi', 'vn', 'vu', 'wf', 'ws', 'ye', 'yt', 'za', 'zm', 'zw'
    ]

    url = re.sub('\/.+$', '', url, 1)
    main_domain = re.sub('^[^\.]+\.', '', url, 1)
    if re.compile('^' + '$|^'.join(top_level_domains) + '$').match(main_domain) != None:
      return url
    if re.compile('^' + '\.|^'.join(top_level_domains) + '\.').match(main_domain) != None:
      return url
    return main_domain

  def strip_url(self, url):
    url = re.sub('(^http\:\/\/)|(^https\:\/\/)', '', url)
    url = re.sub('^www\.', '', url)
    if url[-1] == '/':
      url = url[:-1]
    return url.strip()

  def is_subdomain(self, base_url, href): 
    url_1 = self.get_clean_url(urlparse(base_url).hostname)
    url_2 = self.get_clean_url(urlparse(href).hostname)
    return self.get_main_domain(url_1) == self.get_main_domain(url_2)

  def extract_links(self, base_url, text): 
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.find_all('a'):
      if not a.has_attr('href'): continue
      if len(a['href']) > 0 and a['href'][0] == "#": continue

      href = urljoin(base_url, a['href'])

      if not self.is_subdomain(base_url, href): 
        continue

      url = urlparse(href).geturl()
      UniTrackerThread.lock.acquire()
      self.url_manager.push_url(url)
      UniTrackerThread.lock.release()
   
  def run(self): 
    while (self.url_manager.has_url()):
      UniTrackerThread.lock.acquire()
      base_url = self.url_manager.pop_url()
      UniTrackerThread.lock.release()

      base_url = base_url.strip()
      if len(base_url) == 0:
        time.sleep(1)
        continue

      if re.match('pdf$', base_url) != None:
        continue

      if re.match('^http', base_url) == None:
        base_url = 'http://' + base_url

      proxy = base_url.replace("http://", "").replace("https://", "")
      if len(base_url) == 0:
        continue

      r = None
      error = None
      failed = True
      try:
        r = requests.get(base_url, proxies = { 'http': proxy }, timeout = 5)
        failed = False
      except requests.exceptions.RequestException as e:
        error = e
        print "Failed", base_url, e
        continue;
      print "Downloaded", base_url

      UniTrackerThread.lock.acquire()
      self.url_manager.downloaded_urls[base_url] = True
      UniTrackerThread.lock.release()

      text = r.text.encode('utf-8')
      if proxy.count('/') > 0:
        UniTrackerThread.lock.acquire()
        if self.classifier.Predict(base_url, text):
          print "Faculty:", base_url.strip()
          header = warc.WARCHeader({
            "WARC-Type": "response",
            "WARC-Target-URI": base_url.strip(),
            "Is-Faculty-Repository": "2"
          }, defaults=True)
          warc_record = warc.WARCRecord(header, text)
          warc_f.write_record(warc_record)
        UniTrackerThread.lock.release()

      self.extract_links(base_url, text)
      sys.stdout.flush()

    print "Ended", self.thread_id

url_manager = UrlManager()
def signal_handler(signal, frame):
  print('Finishing...')
  UniTrackerThread.lock.acquire()
  warc_f.close()
  url_manager.save_visited_urls(sys.argv[2])
  url_manager.save_unvisited_urls(sys.argv[3])
  UniTrackerThread.lock.release()
  sys.exit(0)

if __name__ == "__main__":
  if len(sys.argv) == 4:
    warc_f = warc.open(sys.argv[1], "a+")
    url_manager.load_visited_urls(sys.argv[2])
    url_manager.load_unvisited_urls(sys.argv[3])

    threads = []
    for i in range(0, 8):
      t = UniTrackerThread(url_manager, '', i, warc_f)
      t.daemon = True
      threads.append(t)
      t.start()

    signal.signal(signal.SIGINT, signal_handler)
    while True:
      time.sleep(1)

  else:
    print "Usage: uni_crawler.py <warc_file> <visited_urls> <unvisited_urls>"
