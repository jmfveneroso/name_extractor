import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import calibration_curve
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score

import os
import sys
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from tokenizer import Tokenizer
from name_extractor import create_model
from orm import Url, WebPage, ResearchGroup
from random import shuffle

relevant_titles = [
  'faculty', 'staff', 'people', 'lecturers', 'personnel', 
  'professors', 'members', 'professorat', 'professoren',
  'directory', 'equipo', 'news'
]

relevant_text = [
  'dr', 'drs', 'drd', 'mr', 'mrs', 'ms', 'professor', 
  'dipl', 'prof', 'miss', 'emeritus', 'ing', 'assoc', 
  'asst', 'lecturer', 'ast', 'res', 'inf', 'diplom', 
  'jun', 'junprof', 'inform', 'lect', 'senior', 'ass', 
  'ajarn', 'honorarprof', 'theol', 'math', 'phil', 'doz', 
  'dphil', 'senior', 'associate', 'emerita', 'assistant',
  'faculty', 'staff', 'people', 'lecturers', 'personnel', 
  'professors', 'members', 'professorat', 'professoren',
  'directory', 'equipo', 'the', 'news'
]

feature_labels = [
  'url.faculty', 'url.staff', 'url.people', 'url.lecturers', 'url.personnel', 
  'url.professors', 'url.members', 'url.professorat', 'url.professoren',
  'url.directory', 'url.equipo', 'url.news',
  'title.faculty', 'title.staff', 'title.people', 'title.lecturers', 'title.personnel', 
  'title.professors', 'title.members', 'title.professorat', 'title.professoren',
  'title.directory', 'title.equipo', 'title.news',
  'h1.faculty', 'h1.staff', 'h1.people', 'h1.lecturers', 'h1.personnel', 
  'h1.professors', 'h1.members', 'h1.professorat', 'h1.professoren',
  'h1.directory', 'h1.equipo', 'h1.news',
  'h2.faculty', 'h2.staff', 'h2.people', 'h2.lecturers', 'h2.personnel', 
  'h2.professors', 'h2.members', 'h2.professorat', 'h2.professoren',
  'h2.directory', 'h2.equipo', 'h2.news',
  'h3.faculty', 'h3.staff', 'h3.people', 'h3.lecturers', 'h3.personnel', 
  'h3.professors', 'h3.members', 'h3.professorat', 'h3.professoren',
  'h3.directory', 'h3.equipo', 'h3.news',
  'dr', 'drs', 'drd', 'mr', 'mrs', 'ms', 'professor', 
  'dipl', 'prof', 'miss', 'emeritus', 'ing', 'assoc', 
  'asst', 'lecturer', 'ast', 'res', 'inf', 'diplom', 
  'jun', 'junprof', 'inform', 'lect', 'senior', 'ass', 
  'ajarn', 'honorarprof', 'theol', 'math', 'phil', 'doz', 
  'dphil', 'senior', 'associate', 'emerita', 'assistant', 
  'faculty', 'staff', 'people', 'lecturers', 'personnel', 
  'professors', 'members', 'professorat', 'professoren',
  'directory', 'equipo', 'the', 'news',
  'length', 'num_names'
]

tokenizer = Tokenizer()
model = create_model()
class Featurizer:
  def __init__(self, tokenizer, model, url, html):
    self.tokenizer = tokenizer 
    self.m = model
    self.url = url
    self.features = []

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title')

    # print [t.tkn for t in self.tokenizer.tokenize_text(url)]
    self.features = self.features + self.generate_url_features(url.decode('utf-8'))
    self.features = self.features + self.generate_title_features([title])
    self.features = self.features + self.generate_title_features(soup.find_all('h1'))
    self.features = self.features + self.generate_title_features(soup.find_all('h2'))
    self.features = self.features + self.generate_title_features(soup.find_all('h3'))

    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('title')]
    [s.extract() for s in soup('h1')]
    [s.extract() for s in soup('h2')]
    [s.extract() for s in soup('h3')]
    self.features = self.features + self.generate_text_features(soup.find('body'))
    self.m.extract_html_simple(html)

    # Most important feature: number of names found.
    self.features = self.features + [len(self.m.found_names)]
    
    # print [(feature_labels[i], self.features[i]) for i in range(0, len(self.features))]
    # sys.stdout.flush()

  def get_text_from_element(self, element):
    if element == None:
      return ''

    content = ''
    n_strs = [i for i in element.recursiveChildGenerator() if type(i) == NavigableString]
    for n_str in n_strs:
      content += n_str.strip() + ' '
    return content

  def generate_url_features(self, url):
    features = [0] * len(relevant_titles)
    tkns = self.tokenizer.tokenize_url(url)
    for i in range(0, len(relevant_titles)):
      features[i] += len([t for t in tkns if t == relevant_titles[i]])
    return features

  def generate_title_features(self, elements):
    features = [0] * len(relevant_titles)
    for el in elements:
      if el == None:
        continue

      text = self.get_text_from_element(el)
      tkns = [t.tkn for t in self.tokenizer.tokenize(text)]
      for i in range(0, len(relevant_titles)):
        features[i] += len([t for t in tkns if t == relevant_titles[i]])
    return features

  def generate_text_features(self, element):
    features = [0] * (len(relevant_text) + 1)
    if element == None:
      return features

    text = self.get_text_from_element(element)
    tkns = [t.tkn for t in self.tokenizer.tokenize(text)]
    for i in range(0, len(relevant_text)):
      features[i] += len([t for t in tkns if t == relevant_text[i]])

    features[-1] = len(tkns)
    return features

class Classifier:
  def __init__(self):
    self.m = create_model()
    self.model = joblib.load('data/classifier.pkl') 
 
  def Predict(self, url, text):
    web_page = Featurizer(tokenizer, self.m, url, text)
    predicted = self.model.predict([web_page.features])
    return predicted[0]

  def fit(self, filename):
    x = []
    y = []
    url_ids = []
    lines = []
    with open(filename) as f:
      for line in f:
        lines.append(line)

    shuffle(lines)
    for line in lines:
      arr = [int(el) for el in line.strip().split(', ')]
 
      x.append(arr[:-2])
      y.append(arr[-2])
      url_ids.append(arr[-1])

    # m = GaussianNB()
    # m = LogisticRegression()
    # m = LinearSVC(C=1.0)
    m = RandomForestClassifier(n_estimators=100)

    self.model = m.fit(x[:-200], y[:-200])
    x_test = x[-200:]
    y_test = y[-200:]
    # self.model = m.fit(x, y)
    # x_test = x
    # y_test = y 
    predicted = self.model.predict(x_test)
    np.set_printoptions(threshold='nan')
    # print predicted

    errors = 0
    for i in range(0, len(y_test)):
      if predicted[i] != y_test[i]:
        errors += 1
        id = int(WebPage.find(url_ids[i]).values['url_id'])
        print 'Expected', y_test[i], 'url', Url.find(id).values['url'], url_ids[i]

    print 'Errors:', errors, '/', len(y_test)

    scores = cross_val_score(m, x, y, cv=5)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    joblib.dump(self.model, 'data/classifier.pkl') 

  def create_feature_vectors(self, filename):
    feature_vectors = []
    expected_values = []
    web_page_ids = []

    web_pages = WebPage.select_where('is_faculty_repo = TRUE')
    num_pages = len(web_pages)
    count = 1
    for w in web_pages:
      url = Url.find(int(w.values['url_id']))
      v = Featurizer(tokenizer, self.m, url.values['url'], w.values['content']).features
      feature_vectors.append(v)
      expected_values.append(1)
      web_page_ids.append(w.values['id'])
      print 'Faculty:', url.values['url'], count, '/', num_pages
      count += 1

    web_pages = WebPage.select_where('is_faculty_repo = FALSE')
    num_pages = len(web_pages)
    count = 1
    for w in web_pages:
      url = Url.find(int(w.values['url_id']))
      v = Featurizer(tokenizer, self.m, url.values['url'], w.values['content']).features
      feature_vectors.append(v)
      expected_values.append(0)
      web_page_ids.append(w.values['id'])
      print 'Non faculty:', url.values['url'], count, '/', num_pages
      count += 1

    # print '==============================================='
    # for i in range(0, len(feature_vectors)):
    #   v = feature_vectors[i] + [expected_values[i], int(web_page_ids[i])]
    #   print ", ".join([str(el) for el in v])
   
    f = open(filename, 'w')  
    for i in range(0, len(feature_vectors)):
      v = feature_vectors[i] + [expected_values[i], int(web_page_ids[i])]
      f.write(", ".join([str(el) for el in v]) + '\n')
    f.close()

if __name__ == "__main__":
  classifier  = Classifier()
  if len(sys.argv) > 2:
    filename = sys.argv[2]
    if sys.argv[1] == 'fit':
      classifier.fit(filename)
    if sys.argv[1] == 'featurize':
      classifier.create_feature_vectors(filename)
  else:
    print 'usage: classifier.py <fit|featurize> <filename>'
