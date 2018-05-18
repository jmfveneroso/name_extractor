#!/usr/bin/python
# coding=UTF-8

import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString

def c_token(text):
  special_chars = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿšŽčžŠšČłńężść".decode("utf-8")
  chars         = "aaaaaaeceeeeiiiidnoooooxouuuuypsaaaaaaeceeeeiiiionooooooouuuuypysZczSsClnezsc"

  new_text = ""
  for c in text:
    index = special_chars.find(c)
    if index != -1:
      new_text += chars[index]
    else:
      new_text += c
  return new_text

class Token():
  def __init__(self, tkn, element, is_first_tkn, last_tkn, next_tkn, word_pos):
    self.tkn = tkn
    self.element = element
    self.is_first_tkn = is_first_tkn
    self.last_tkn = last_tkn
    self.next_tkn = next_tkn
    self.is_name = False
    self.is_first_name = False
    self.next_tkn = next_tkn
    self.word_pos = word_pos

    second_parent_name = ''
    if element.parent != None:
      second_parent_name = element.parent.name

    third_parent_name = ''
    if element.parent != None and element.parent.parent != None:
      third_parent_name = element.parent.parent.name

    el = element
    self.class_name = ""
    while element != None:
      if element.has_attr("class"):
        try:
          self.class_name = c_token(" ".join(element.get("class")).encode('utf-8'))
        except:
          break
        break
      element = element.parent
    # if element.has_attr('class'):
    #   self.class_name = " ".join(element.get("class"))

    self.parent = second_parent_name + el.name
    self.second_parent = second_parent_name
    self.third_parent = third_parent_name

    self.text_depth = 0
    element = el
    while element != None:
      element = element.parent
      self.text_depth += 1

    element = el
    self.element_position = 0
    if element.parent != None:
      for child in element.parent.findChildren():
        if child == element:
          break
        self.element_position += 1

class Tokenizer():
  def remove_emails(self, text):
    text = re.sub('\S+@\S+(\.\S+)+', '', text)
    text = re.sub('\S\S\S+\.\S\S\S+', '', text)
    return text
  
  def remove_urls(self, text):
    regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(regex, '', text)
  
  def remove_titles(self, text):
    text = re.sub('(M\. Sc\.)|(M\.Sc\.)|(MS\. SC\.)|(MS\.SC\.)', '', text)
    text = re.sub('(M\. Sc)|(M\.Sc)|(MS\. SC)|(MS\.SC)', '', text)
    text = re.sub('(M\. Ed\.)|(M\.Ed\.)|(M\. ED\.)|(M\.ED\.)', '', text)
    text = re.sub('(M\. Ed)|(M\.Ed)|(M\. ED)|(M\.ED)', '', text)
    text = re.sub('(sc\. nat\.)|(sc\.nat\.)', '', text)
    text = re.sub('(rer\. nat\.)|(rer\.nat\.)|(rer nat)|(rer\. nat)', '', text)
    text = re.sub('(i\. R\.)', '', text)
    text = re.sub('(PD )|( PD )', '', text)
    text = re.sub('(Sc\. Nat\.)|(Sc\.Nat\.)|(SC\. NAT\.)|(SC\.NAT\.)', '', text)
    text = re.sub('(Sc\. Nat)|(Sc\.Nat)|(SC\. NAT)|(SC\.NAT)', '', text)
    text = re.sub('(MD\.)|(Md\.)|(Md )', '', text)
    text = re.sub('(B\. Sc\.)|(B\.Sc\.)|(BS\. SC\.)|(BS\.SC\.)', '', text)
    text = re.sub('(B\. Sc)|(B\.Sc)|(BS\. SC)|(BS\.SC)', '', text)
    text = re.sub('(Ph\. D\.)|(Ph\.D\.)|(PH\. D\.)|(PH\.D\.)', '', text)
    text = re.sub('(Ph\. D)|(Ph\.D)|(PH\. D)|(PH\.D)', '', text)
    text = re.sub('(Ed\. D\.)|(Ed\.D\.)|(ED\. D\.)|(ED\.D\.)', '', text)
    text = re.sub('(Ed\. D)|(Ed\.D)|(ED\. D)|(ED\.D)', '', text)
    text = re.sub('(M\. S\.)|(M\.S\.)', '', text)
    text = re.sub('(M\. S)|(M\.S)', '', text)
    text = re.sub('(Hon\.)', '', text)
    text = re.sub('(a\.D\.)', '', text)
    text = re.sub('(em\.)', '', text)
    text = re.sub('(apl\.)|(Apl\.)', '', text)
    return text

  def convert_token(self, text):
    special_chars = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿšŽčžŠšČłńężść".decode("utf-8")
    chars         = "aaaaaaeceeeeiiiidnoooooxouuuuypsaaaaaaeceeeeiiiionooooooouuuuypysZczSsClnezsc"
  
    new_text = ""
    for c in text:
      index = special_chars.find(c)
      if index != -1:
        new_text += chars[index]
      else:
        new_text += c
    return new_text
  
  def tokenize_url(self, url):
    text = self.convert_token(url.strip()).lower()
    if len(text) == 0 or text == None:
      return [];
   
    return re.compile("[^a-zA-Z0-9]+").split(text)
  
  def tokenize_text(self, text):
    text = self.remove_urls(text)
    text = self.remove_titles(text)
    text = self.remove_emails(text)
    text = self.convert_token(text.strip()).lower()
    if len(text) == 0 or text == None:
      return [];
   
    return re.compile("[^a-zA-Z0-9]+").split(text)

  def tokenize(self, html):
    result = []
    soup = BeautifulSoup(html, 'html.parser')

    # Remove code elements.
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    for br in soup.find_all("br"):
      if len(br.findChildren()) == 0:
        br.replace_with(" linebreak ")

    # Iterate through all text elements.
    n_strs = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
    for n_str in n_strs:
      content = n_str.strip()
      if len(content) == 0 or content == None:
        continue;

      # Tokenize content and remove double spaces.
      tkns = self.tokenize_text(content)
      tkns = [t for t in tkns if (len(t) > 0 and re.match("^\S+$", t) != None)]
      if len(tkns) == 0:
        continue

      last_tkn = None
      cur_tkn = None
      for i in range(0, len(tkns)):
        cur_tkn = Token(tkns[i], n_str.parent, i == 0, last_tkn, None, i)
        if last_tkn != None:
          last_tkn.next_tkn = cur_tkn
        last_tkn = cur_tkn
        result.append(cur_tkn)

    return result

  def get_num_repeated_elements(self, tokens):
    el = tokens[0].element
    for i in range(1, len(tokens)):
      if tokens[i].element != el:
        return i - 1
    return 3
