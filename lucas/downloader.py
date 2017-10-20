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

class DownloaderThread(threading.Thread):
  lock = threading.Lock()

  def __init__(self, url_manager, output_dir, thread_id):
    threading.Thread.__init__(self)
    self.url_manager = url_manager
    self.thread_id = thread_id
    self.output_dir = output_dir

  def run(self): 
    DownloaderThread.lock.acquire()
    print "Starting thread", self.thread_id
    DownloaderThread.lock.release()

    while (self.url_manager.has_url()):
      DownloaderThread.lock.acquire()
      base_url = self.url_manager.pop_url()
      DownloaderThread.lock.release()

      url_id = base_url[0]
      base_url = base_url[1].strip()
      proxy = base_url.replace("http://", "").replace("https://", "")
      proxies = { 'http': proxy }

      r = None
      try:
        r = requests.get(base_url, proxies = { 'http': proxy }, timeout = 5)
      except:
        DownloaderThread.lock.acquire()
        print "Failed downloading", base_url, "with id", url_id
        DownloaderThread.lock.release()
        continue;

      dir = os.path.dirname(__file__)
      filename = os.path.join(os.path.dirname(__file__), self.output_dir, str(url_id) + ".html")
      with open(filename, "w") as f:
        f.write(r.text.encode('utf8'))
      DownloaderThread.lock.acquire()
      print "Written file", base_url, "with id", url_id
      DownloaderThread.lock.release()

    sys.stdout.flush()

if __name__ == "__main__":
  start_time = time.time()

  url_manager = UrlManager()
  url_manager.push_url("https://www.soic.indiana.edu/all-people/index.html")
  url_manager.push_url("http://eng.auburn.edu/ece/faculty/")
  url_manager.push_url("https://cs.illinois.edu/people/faculty/department-faculty")
  url_manager.push_url("https://www.cics.umass.edu/people/all-faculty-staff")
  url_manager.push_url("http://ee.princeton.edu/people/faculty")
  url_manager.push_url("http://www.swosu.edu/common/people-search/public/business-computer-science.php")
  url_manager.push_url("http://www.uncw.edu/csc/about/facultystaff.html")
  url_manager.push_url("http://salisbury.edu/mathcosc/dept-directory-old.html")

  threads = []
  for i in range(0, 8):
    t = DownloaderThread(url_manager, sys.argv[1], i)
    threads.append(t)
    t.start()
    time.sleep(1)

  for t in threads:
    t.join()

  print 'The process took', time.time() - start_time, 'seconds.'
