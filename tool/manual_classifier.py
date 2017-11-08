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

data = ''
class GetHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    # self.wfile.write(data)
    self.wfile.write('dawdwda')
    return

  def log_message(self, format, *args):
    return

def serve():
  server = HTTPServer(('localhost', 8080), GetHandler)
  server.serve_forever()

if __name__ == "__main__":
  if len(sys.argv) == 3:
    t1 = threading.Thread(target=serve)
    t1.daemon = True
    t1.start()

    is_faculty = int(raw_input('Is faculty:'))
    
    # in_warc = warc.open(sys.argv[1], "r")
    # out_warc = warc.open(sys.argv[2], "w")
    # for record in in_warc:
    #   is_faculty = int(record['Is-Faculty-Repository'])
    #   if is_faculty == 2:
    #     print record.url
    #     data = record.payload.read()
    #     is_faculty = int(raw_input('Is faculty:'))

    #   header = warc.WARCHeader({
    #     "WARC-Type": "response",
    #     "WARC-Target-URI": record.url,
    #     "Is-Faculty-Repository": str(is_faculty)
    #   }, defaults=True)
    #   warc_record = warc.WARCRecord(header, data)
    #   out_warc.write_record(warc_record)

    # in_warc.close()
    # out_warc.close()

  else:
    print "Usage: manual_classifier.py <warc_file>"
