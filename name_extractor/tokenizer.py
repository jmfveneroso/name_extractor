#!/usr/bin/python
# coding=UTF-8

import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString

class HtmlToken():
  """ 
  An HTML token is a composite object containing a value, and
  the corresponding HTML element from where that value was extracted.
  It also holds a list of textual and structural features.
  """

  def __init__(self, tkn, element):
    self.tkn = tkn
    self.element = element

    # Textual features can be generalized whereas structural
    # features are only useful on a per document basis. Therefore they
    # must be estimated for each HTML document on a second run.
    self.textual_features = []
    self.structural_features = []

    self.is_name = False
    self.is_first_name = False

  def set_structural_features(self, features):
    self.structural_features = features

class Tokenizer():
  def remove_emails(self, text):
    """ 
    Removes emails from a string. 
    """
    # The Regex is a simplified version of the one that would account 
    # for all emails, but it is good enough for most cases.
    text = re.sub('\S+@\S+(\.\S+)+', '', text)

    # Sometimes the domain is omitted from the email.
    text = re.sub('\S\S\S+\.\S\S\S+', '', text)
    return text
  
  def remove_urls(self, text):
    """ 
    Removes urls from a string. 
    """
    regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(regex, '', text)
  
  def remove_titles(self, text):
    """ 
    Removes academic titles from a string. 
    """
    text = re.sub('(M\. Sc\.)|(M\.Sc\.)|(MS\. SC\.)|(MS\.SC\.)', '', text)
    # text = re.sub('(M\. Sc)|(M\.Sc)|(MS\. SC)|(MS\.SC)', '', text)
    text = re.sub('(M\. Ed\.)|(M\.Ed\.)|(M\. ED\.)|(M\.ED\.)', '', text)
    # text = re.sub('(M\. Ed)|(M\.Ed)|(M\. ED)|(M\.ED)', '', text)
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
    # text = re.sub('(M\. S)|(M\.S)', '', text)
    text = re.sub('(Hon\.)', '', text)
    text = re.sub('(a\.D\.)', '', text)
    text = re.sub('(em\.)', '', text)
    text = re.sub('(apl\.)|(Apl\.)', '', text)
    return text

  def convert_accented_characters(self, text):
    """ 
    Converts accented characters in a string to their unaccented forms.
    The string is assumed to be in UTF-8 form.
    """
    # TODO: we should account for other types of encodings and remove all
    # strange characters.
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
  
  def tokenize_text(self, text):
    """ 
    Extracts a list of textual tokens from a string, ignoring
    urls, titles and emails.
    """
    text = self.remove_urls(text)
    text = self.remove_titles(text)
    text = self.remove_emails(text)
    text = self.convert_accented_characters(text.strip()).lower()
    if len(text) == 0 or text == None:
      return [];
   
    return re.compile("[^a-zA-Z0-9]+").split(text)

  def get_parent(self, element):
    """ 
    Returns the parent tag of an HTML element.
    """
    if element.parent != None:
      return self.convert_accented_characters(element.parent.name)
    return ''

  def get_second_parent(self, element):
    """ 
    Returns the second parent tag of an HTML element.
    """
    if element.parent != None:
      if element.parent.parent != None:
        return self.convert_accented_characters(element.parent.parent.name)
    return ''

  def get_class_name(self, element):
    """ 
    Returns the class name of an HTML element. If the element has
    no class, then the innermost parent class name is returned instead.
    """
    while element != None:
      if element.has_attr("class"):
        try:
          class_name = " ".join(element.get("class")).encode('utf-8')
          return self.convert_accented_characters(class_name)
        except:
          break
        break
      element = element.parent
    return ''

  def get_text_depth(self, element):
    """ 
    Returns the number of "indents" in the DOM Tree until the HTML
    element is reached.
    """
    text_depth = 0
    while element != None:
      element = element.parent
      text_depth += 1
    return text_depth

  def get_element_position(self, element):
    """ 
    Returns the position of an HTML element in comparison with its siblings 
    relative to the HTML parent element.
    """
    element_position = 0
    if element.parent != None:
      for child in element.parent.findChildren():
        if child == element:
          break
        element_position += 1
    return element_position

  def create_token(self, tkn_value, element):
    """ 
    Creates an HTML token from a token value and the enclosing
    HTML element. Also calculates the structural features for that token.
    """
    tkn = HtmlToken(tkn_value, element)
    tkn.set_structural_features([
      self.get_parent(element), 
      self.get_second_parent(element), 
      self.get_class_name(element), 
      self.get_text_depth(element), 
      self.get_element_position(element)
    ])

    return tkn

  def assign_correct_labels(self, tokens, correct_names):
    """ 
    Assigns the correct labels (name or word) to a list of HtmlTokens.
    """
    correct_names = [n.split(' ') for n in correct_names]

    i = 0
    while i < len(tokens):
      size = 0
      for name in correct_names: 
        match = True
        for j in range(0, len(name)):
          if i + j >= len(tokens) or tokens[i + j].tkn != name[j]:
            match = False
            break
        if match:
          size = len(name)  
          break

      if size == 0:
        i += 1
      else:
        tokens[i].is_first_name = True
        for j in range(i, i + size):
          tokens[j].is_name = True
        i += size

  def tokenize(self, html, correct_names):
    """ 
    Returns a list of HtmlTokens extracted from an HTML document.
    """
    result = []
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style tags.
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    for br in soup.find_all("br"):
      if len(br.findChildren()) == 0:
        br.replace_with(" linebreak ")

    # Iterate through all text elements.
    n_strs = [i for i in soup.recursiveChildGenerator() if type(i) == NavigableString]
    for n_str in n_strs:
      content = n_str.strip()
      if len(content) == 0 or content is None:
        continue;

      # Tokenize content and remove double spaces.
      tkns = self.tokenize_text(content)
      tkns = [t for t in tkns if (len(t) > 0 and re.match("^\S+$", t) != None)]

      for i in range(0, len(tkns)):
        tkn = self.create_token(tkns[i], n_str.parent)
        result.append(tkn)
 
    # TODO: The removal of all titles should be moved to the remove_titles function.
    result = [t for t in result if not t.tkn in [
      'dr', 'drs', 'drd', 'mr', 'mrs', 'ms', 'professor', 'dipl', 'prof', 
      'miss', 'emeritus', 'ing', 'assoc', 'asst', 'lecturer', 'ast', 'res', 
      'inf', 'diplom', 'jun', 'junprof', 'inform', 'lect', 'senior', 'ass', 
      'ajarn', 'honorarprof', 'theol', 'math', 'phil', 'doz', 'dphil', 'ir'
    ]]
    result = [t for t in result if re.search('[0-9]', t.tkn) == None]
    self.assign_correct_labels(result, correct_names)
    return result
