import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import calibration_curve

import os
import sys
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from tokenizer import Tokenizer
from name_extractor import create_model

relevant_titles = [
  'faculty', 'staff', 'people', 'lecturers', 'personnel', 
  'professors', 'members', 'professorat', 'professoren',
  'directory', 'equipo'
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
  'directory', 'equipo'
]

feature_labels = [
  'url.faculty', 'url.staff', 'url.people', 'url.lecturers', 'url.personnel', 
  'url.professors', 'url.members', 'url.professorat', 'url.professoren',
  'url.directory', 'url.equipo',
  'title.faculty', 'title.staff', 'title.people', 'title.lecturers', 'title.personnel', 
  'title.professors', 'title.members', 'title.professorat', 'title.professoren',
  'title.directory', 'title.equipo',
  'h1.faculty', 'h1.staff', 'h1.people', 'h1.lecturers', 'h1.personnel', 
  'h1.professors', 'h1.members', 'h1.professorat', 'h1.professoren',
  'h1.directory', 'h1.equipo',
  'h2.faculty', 'h2.staff', 'h2.people', 'h2.lecturers', 'h2.personnel', 
  'h2.professors', 'h2.members', 'h2.professorat', 'h2.professoren',
  'h2.directory', 'h2.equipo',
  'h3.faculty', 'h3.staff', 'h3.people', 'h3.lecturers', 'h3.personnel', 
  'h3.professors', 'h3.members', 'h3.professorat', 'h3.professoren',
  'h3.directory', 'h3.equipo',
  'dr', 'drs', 'drd', 'mr', 'mrs', 'ms', 'professor', 
  'dipl', 'prof', 'miss', 'emeritus', 'ing', 'assoc', 
  'asst', 'lecturer', 'ast', 'res', 'inf', 'diplom', 
  'jun', 'junprof', 'inform', 'lect', 'senior', 'ass', 
  'ajarn', 'honorarprof', 'theol', 'math', 'phil', 'doz', 
  'dphil', 'senior', 'associate', 'emerita', 'assistant', 
  'faculty', 'staff', 'people', 'lecturers', 'personnel', 
  'professors', 'members', 'professorat', 'professoren',
  'directory', 'equipo',
  'length', 'num_names'
]

class WebPage:
  def __init__(self, tokenizer, model, url, filename):
    self.tokenizer = tokenizer 
    self.model = model
    self.url = url
    print url
    self.features = []
    with open(filename) as f:
      html =  f.read()
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
      self.model.extract(filename)

      # Most important feature: number of names found.
      self.features = self.features + [len(self.model.found_names)]
     
      print [(feature_labels[i], self.features[i]) for i in range(0, len(self.features))]

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

if __name__ == "__main__":
  tokenizer = Tokenizer()
  model = create_model()

  # Faculty
  faculty_path = "downloaded_pages/faculty/"
  files = [f for f in os.listdir(faculty_path) if os.path.isfile(os.path.join(faculty_path, f))]

  faculty_features = [[]] * 216
  urls = [0] * 216
  with open('data/faculty_pages.txt') as f: 
    i = 0
    for line in f:
      urls[i] = line.strip()
      i += 1

  for i in range(1, 217):
    num = str(i).zfill(3)
    # num = int(f[:3])
    f = str(num) + '.html'
    print f
    if os.path.isfile(os.path.join(faculty_path, f)):
      web_page = WebPage(tokenizer, model, urls[i - 1], faculty_path + f)
      faculty_features[i - 1] = web_page.features

  print '================================================='
  for features in faculty_features:
    print ', '.join([str(f) for f in features])
  

  # Non Faculty
  # non_faculty_path = "../name_extractor_data/non_faculty/"
  # files = [f for f in os.listdir(non_faculty_path) if os.path.isfile(os.path.join(non_faculty_path, f))]

  # non_faculty_features = [[]] * 1174
  # urls = [0] * 1174
  # with open('data/non_faculty_pages.txt') as f: 
  #   i = 0
  #   for line in f:
  #     urls[i] = line.strip()
  #     i += 1

  # for i in range(1, 1175):
  #   num = str(i)
  #   f = str(num) + '.html'
  #   print f
  #   if os.path.isfile(os.path.join(non_faculty_path, f)):
  #     web_page = WebPage(tokenizer, model, urls[i - 1], non_faculty_path + f)
  #     non_faculty_features[i - 1] = web_page.features

  # print '================================================='
  # for features in non_faculty_features:
  #   print ', '.join([str(f) for f in features])


  # Classifier.
  # faculty_data = []
  # non_faculty_data = []

  # data_path = "data/"
  # faculty_file = data_path + 'faculty_classifier_features.txt'
  # non_faculty_file = data_path + 'non_faculty_classifier_features.txt'
  # with open(faculty_file) as f: 
  #   for line in f:
  #     if len(line) > 1:
  #       faculty_data.append([int(x) for x in line.split(', ')])

  # with open(non_faculty_file) as f: 
  #   for line in f:
  #     if len(line) > 1:
  #       non_faculty_data.append([int(x) for x in line.split(', ')])

  # x = non_faculty_data[:-100] + faculty_data[:-20]
  # y = [0] * (len(non_faculty_data) - 100)
  # y = y + [1] * (len(faculty_data) - 20)

  # x_test = non_faculty_data[-100:] + faculty_data[-20:]
  # y_test = [0] * 100 + [1] * 20

  # # Create classifiers
  # # m = GaussianNB()
  # # m = LogisticRegression()
  # # m = LinearSVC(C=1.0)
  # m = RandomForestClassifier(n_estimators=100)
  # 
  # model = m.fit(x, y)
 
  # x_test = x
  # y_test = y 
  # predicted = model.predict(x_test)
  # np.set_printoptions(threshold='nan')
  # print predicted
  # errors = 0
  # for i in range(0, len(y_test)):
  #   if predicted[i] != y_test[i]:
  #     errors += 1

  #     if i > len(non_faculty_data) - 100:
  #       print "Errou faculty", i - len(non_faculty_data) + 100
  #     else:
  #       print "Errou non faculty", i
  # print 'Errors:', errors, '/', len(y_test)
