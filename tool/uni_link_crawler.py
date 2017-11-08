#!/usr/bin/python
# coding=UTF-8

import os
import sys
import time
import re
import requests
import datetime
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup

nums = [42,15,31,2,17,2,88,12,51,46,26,1,12,80,2,36,44,5,4,1,2,32,15,8,167,3,36,2,50,9,22,13,142,7,2,1,1,66,393,102,1,16,1,33,3,9,13,16,28,31,1,6,28,43,44,25,1,1,10,31,1,4,32,266,1,1,2,3,12,281,26,50,1,1,1,2,16,4,4,6,6,10,12,37,10,382,181,200,50,24,22,93,3,568,28,28,50,1,147,12,8,15,5,22,24,1,1,12,2,17,2,4,7,6,21,154,3,1,3,1,1,2,158,12,1,10,1,1,29,16,4,12,46,5,1,10,18,1,120,1,23,12,131,16,17,5,13,68,123,132,63,26,2,1,62,316,11,5,1,1,2,1,65,10,13,2,3,6,33,4,1,16,22,3,84,25,38,1,1,37,51,15,86,3,22,69,1,1,1,3,19,89,1,1,19,77,37,171,6,25,37,50,1,14,8,15]

countries = ['af','al','dz','ad','ao','ag','ar','am','au','at','az','bs','bh','bd','bb','by','be','bz','bj','bm','bt','bo','ba','bw','br','bn','bg','bf','mm','bi','kh','cm','ca','cv','ky','cf','td','cl','cn','co','km','cd','cg','cr','ci','hr','cu','cy','cz','dk','dj','dm','do','ec','eg','sv','gq','er','ee','et','fo','fj','fi','fr','gf','pf','ga','gm','ge','de','gh','gr','gl','gd','gp','gu','gt','gn','gy','ht','va','hn','hk','hu','is','in','id','ir','iq','ie','il','it','jm','jp','jo','kz','ke','kp','kr','kv','kw','kg','la','lv','lb','ls','lr','ly','li','lt','lu','mo','mk','mg','mw','my','mv','ml','mt','mq','mr','mu','mx','md','mc','mn','me','ms','ma','mz','na','np','nl','an','nc','nz','ni','ne','ng','nu','no','om','pk','ps','pa','pg','py','pe','ph','pl','pt','pr','qa','re','ro','ru','rw','kn','lc','vc','ws','sm','sa','sn','rs','sc','sl','sg','sk','si','sb','so','za','ss','es','lk','sd','sr','sz','se','ch','sy','tw','tj','tz','th','tl','tg','to','tt','tn','tr','tm','tc','ug','ua','ae','uk','uy','uz','ve','vn','vi','ye','zm','zw']

american_url = 'https://univ.cc/search.php?dom=edu&key=&start='
american_num = 2063

if __name__ == "__main__":
  for j in range(0, len(countries)):
    print "========================================="
    print countries[j], '(', nums[j], ')'
    print "========================================="
    i = 1
    while(i <= nums[j]):
      url = 'https://univ.cc/search.php?dom=' + countries[j] + '&key=&start=' + str(i)
      r = None
      error = None
      try:
        r = requests.get(url, timeout = 5)
      except requests.exceptions.RequestException as e:
        error = e
        print "Failed", url, e
        quit()

      text = r.text.encode('utf-8')
      soup = BeautifulSoup(text, 'html.parser')
      tr = soup.find_all('ol')[0]
      for a in tr.find_all('a'):
        if not a.has_attr('href'): continue
        if len(a['href']) > 0 and a['href'][0] == "#": continue

        href = urlparse(urljoin(url, a['href'])).geturl().encode('utf-8')
        text = ''.join(a.findAll(text=True)).encode('utf-8')
        print href, text

      i += 50
