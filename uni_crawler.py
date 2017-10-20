#!/usr/bin/python
# coding=UTF-8

import os
import sys
import time
import threading
import requests
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup

class UrlManager():
  def __init__(self):
    self.urls = []
    self.visited_urls = {}
    self.url_counter = 1

  def push_url(self, url): 
    if not (url in self.visited_urls):
      self.urls = [(self.url_counter, url)] + self.urls
      self.visited_urls[url] = True
      self.url_counter += 1

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

class UniTrackerThread(threading.Thread):
  lock = threading.Lock()

  def __init__(self, url_manager, output_dir, thread_id):
    threading.Thread.__init__(self)
    self.url_manager = url_manager
    self.thread_id = thread_id
    self.output_dir = output_dir

  def run(self): 
    UniTrackerThread.lock.acquire()
    print "Starting thread", self.thread_id
    UniTrackerThread.lock.release()

    while (self.url_manager.has_url()):
      base_url = self.url_manager.pop_url()
      url_id = base_url[0]
      base_url = base_url[1].strip()
      proxy = base_url.replace("http://", "").replace("https://", "")
      proxies = { 'http': proxy }

      r = None
      try:
        r = requests.get(base_url, proxies = { 'http': proxy }, timeout = 5)
      except:
        print "Failed downloading", base_url, "with id", url_id
        continue;
      print "Downloaded", base_url, "with id", url_id

      dir = os.path.dirname(__file__)
      filename = os.path.join(os.path.dirname(__file__), self.output_dir, str(url_id) + ".html")
      with open(filename, "w") as f:
        f.write(r.text.encode('utf8'))

      # Extract links.
      # soup = BeautifulSoup(r.text, 'html.parser')
      # for a in soup.find_all('a'):
      #   if a.has_attr('href'):
      #     if a['href'][0] == "#":
      #       continue

      #     href = urljoin(base_url, a['href'])
      #     if urlparse(base_url).hostname == urlparse(href).hostname:
      #       self.url_manager.push_url(urlparse(href).geturl())
      #       # print urlparse(href).geturl(), ''.join(a.findAll(text=True))

    sys.stdout.flush()

if __name__ == "__main__":
  start_time = time.time()

  url_manager = UrlManager()
  url_manager.load_from_file(sys.argv[1])

  threads = []
  for i in range(0, 32):
    t = UniTrackerThread(url_manager, sys.argv[2], i)
    threads.append(t)
    t.start()
    time.sleep(1)

  for t in threads:
    t.join()

  print 'The process took ', time.time() - start_time, 'seconds.'
