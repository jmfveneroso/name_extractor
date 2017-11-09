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
import heapq
import warc
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from orm import Url, WebPage, ResearchGroup

data = ''
class GetHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(data)
    return

  def log_message(self, format, *args):
    return

def serve():
  server = HTTPServer(('localhost', 8080), GetHandler)
  server.serve_forever()

if __name__ == "__main__":
  t1 = threading.Thread(target=serve)
  t1.daemon = True
  t1.start()

  while True:
    num = web_page = WebPage.get_num_unknown()
    print 'There are', num, 'unknown pages'
    if num == 0: break

    web_page = WebPage.get_first_unknown()

    url = Url.find(int(web_page.values['url_id']))
    if url == None:
      print 'Error'
      quit()

    print 'Classify', url.values['url'], 'with id', web_page.values['id']
    data = web_page.values['content']
    is_faculty = int(raw_input('Is faculty:'))

    if is_faculty == 1:
      web_page.values['is_faculty_repo'] = 'TRUE'
    else:
      web_page.values['is_faculty_repo'] = 'FALSE'
    web_page.update()
    print 'Webpage', url.values['url'], 'was updated'

  print 'There are no more unknown pages'
