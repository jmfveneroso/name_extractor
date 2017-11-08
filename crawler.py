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
from orm import Url, WebPage, ResearchGroup
import find_dblp_researcher

def strip_url(url):
  url = re.sub('(^http\:\/\/)|(^https\:\/\/)', '', url)
  url = re.sub('^www\.', '', url)
  if url == None or len(url) == 0:
    return ''

  if url[-1] == '/':
    url = url[:-1]
  return url.strip()

def get_main_domain(url): 
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
    return strip_url(url)
  if re.compile('^' + '\.|^'.join(top_level_domains) + '\.').match(main_domain) != None:
    return strip_url(url)
  return strip_url(main_domain)

# Scheduler.
class UrlManager():
  def push_url(self, url): 
    try:
      url.decode('ascii')
    except UnicodeEncodeError, UnicodeDecodeError:
      return

    url = strip_url(url)
    main_domain = get_main_domain(url)

    # Check if url belongs to one of the research group websites.
    rg = ResearchGroup.find_by_url(main_domain)
    if rg == None:
      return

    # Check if the url was already added to the database.
    if Url.find_by_url(url) == None:
      host = strip_url(urlparse(url).hostname)

      scheduled_time = datetime.datetime.utcnow()
      if len(host) > 0:
        host_url = Url.find_by_url(host)
        if host_url == None:
          host_url = Url.create({
            'url': host
          })
          
        s_time = '2017-10-10 00:00:00'
        if host_url.values['scheduled_time'] != None:
          s_time = host_url.values['scheduled_time']
        date_time = datetime.datetime.strptime(s_time, '%Y-%m-%d %H:%M:%S')

        scheduled_time = date_time.utcnow() + datetime.timedelta(0, 3)
        scheduled_time = str(scheduled_time)[:-7]
        host_url.values['scheduled_time'] = scheduled_time
        host_url.update()

      Url.create({
        'url': url,
        'scheduled_time': scheduled_time,
        'crawled': 'FALSE',
        'research_group_id': rg.values['id'],
        'domain': main_domain
      })
    
  def pop_url(self): 
    url = Url.get_next_uncrawled_url()
    if url != None:
      url.values['crawled'] = 'TRUE'
      url.update()
      return url.values['url']
    return ""

  def has_url(self): 
    url = Url.get_next_uncrawled_url()
    return url != None

class UniTrackerThread(threading.Thread):
  lock = threading.Lock()

  def __init__(self, url_manager, thread_id):
    threading.Thread.__init__(self)
    self.url_manager = url_manager
    self.thread_id = thread_id
    self.classifier = Classifier()

  def is_subdomain(self, base_url, href): 
    url_1 = strip_url(urlparse(base_url).hostname)
    url_2 = strip_url(urlparse(href).hostname)
    return get_main_domain(url_1) == get_main_domain(url_2)

  def extract_links(self, base_url, text): 
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.find_all('a'):
      if not a.has_attr('href'): continue
      if len(a['href']) > 0 and a['href'][0] == "#": continue

      href = urljoin(base_url, a['href'])

      if not self.is_subdomain(base_url, href): 
        continue

      url = urlparse(href).geturl()
      self.url_manager.push_url(url)

  def set_downloaded(self, url): 
    url = strip_url(url)
    u = Url.find_by_url(url)
    if u == None:
      raise Exception('Url %s is not in the database.' % (url))
    u.values['download_time'] = str(datetime.datetime.utcnow())[:-7]
    u.update()

  def set_failed(self, url): 
    url = strip_url(url)
    u = Url.find_by_url(url)
    if u == None:
      raise Exception('Url %s is not in the database.' % (url))
    u.values['failed'] = 'TRUE'
    u.update()
   
  def save_html(self, url, content):
    url = strip_url(url)
    u = Url.find_by_url(url)
    if u == None:
      raise Exception('Url %s is not in the database.' % (url))

    WebPage.create({
      'url_id': u.values['id'],
      'content': content
    })

  def run(self): 
    while (True):
      UniTrackerThread.lock.acquire()
      if not self.url_manager.has_url(): 
        UniTrackerThread.lock.release()
        break
      sys.stdout.flush()
      UniTrackerThread.lock.release()

      UniTrackerThread.lock.acquire()
      base_url = self.url_manager.pop_url()
      UniTrackerThread.lock.release()
      print "Url:", base_url

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
        UniTrackerThread.lock.acquire()
        self.set_failed(base_url)
        UniTrackerThread.lock.release()
        print "Failed", base_url, e
        continue;
      print "Downloaded", base_url

      UniTrackerThread.lock.acquire()
      self.set_downloaded(base_url)
      UniTrackerThread.lock.release()

      text = r.text.encode('utf-8')
      if proxy.count('/') > 0:
        if self.classifier.Predict(base_url, text):
          print "Faculty:", base_url.strip()
          UniTrackerThread.lock.acquire()
          self.save_html(base_url, text)
          UniTrackerThread.lock.release()

      UniTrackerThread.lock.acquire()
      self.extract_links(base_url, text)
      UniTrackerThread.lock.release()

    print "Ended", self.thread_id

url_manager = UrlManager()
def signal_handler(signal, frame):
  print('Finishing...')
  UniTrackerThread.lock.acquire()
  UniTrackerThread.lock.release()
  sys.exit(0)

if __name__ == "__main__":
  threads = []
  for i in range(0, 8):
    t = UniTrackerThread(url_manager, i)
    t.daemon = True
    threads.append(t)
    t.start()
  
  signal.signal(signal.SIGINT, signal_handler)
  while True:
    time.sleep(1)
