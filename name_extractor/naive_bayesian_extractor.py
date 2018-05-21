# coding=UTF-8

import os
import re
from math import log

class NaiveBayesianExtractor():
  """ 
  The naive bayesian extractor extracts names from a list of tokens by
  attributing labels with a naive bayesian classifier.
  TODO: this class is a special case of the complex extractor. The
  window size there should be variable.
  """

  def __init__(self):
    # The conditional name P(t|N) and word probabilities P(t|W) were estimated 
    # offline through maximum likelihood over two corpora containing only names 
    # and only words, respectively.
    self.cond_name_probs = {}
    self.cond_word_probs = {}

    # Prior probabilities for each one of these sequences will be estimated 
    # from the test data.
    self.prior_probs = [0] * 2

    # Load the conditional probabilities from a file.
    self.load_conditional_probs()

  def laplace_smoothing(self, count, total_count, possibilities):
    """ 
    Returns a smoothed probability through the Laplace or Additive Smoothing 
    method. More information here: 
    https://en.wikipedia.org/wiki/Additive_smoothing
    """
    return float(count + 1) / (total_count + possibilities)

  def fit(self, docs):
    """ 
    Estimates the prior probabilities from a list of test documents.
    """
    if len(docs) == 0:
      self.load_prior_probs()
      return

    self.prior_probs = [0] * 2
    num_tkns = 0

    for doc in docs:
      tkns = doc[1]
      for t in tkns:
        if t.is_name:
          self.prior_probs[1] += 1
        else:
          self.prior_probs[0] += 1
        num_tkns += 1

    # Compute prior probabilities.
    for i in range(0, 2):
      self.prior_probs[i] = log(self.laplace_smoothing(
        self.prior_probs[i], num_tkns, 2
      ))
    print self.prior_probs

  def load_prior_probs(self, directory = "../probabilities"):
    with open(os.path.join(directory, "naive_bayes_prior_probs.txt")) as f:
      for i in range(0, 2):
        prob = f.readline().split(" ")[1]
        self.prior_probs[i] = float(prob.strip())

  def load_conditional_probs(self, directory = "../probabilities"):
    """ 
    Loads conditional probabilities P(t|W) and P(t|N) from a file. The
    P(t|N) probabilities used in this code sample were estimated from a
    list of author names obtained from the DBLP database. The P(t|W)
    probabilities were estimated from text extracted from random websites
    downloaded with a crawler that started from university homepages. All
    capitalized words were removed as a heuristic to remove all names.
    """
    # Conditional name probabilities.
    with open(os.path.join(directory, "cond_name_probs.txt")) as f:
      for line in f:
        name, prob = line.split(" ")
        self.cond_name_probs[name] = float(prob.strip())

    # Conditional word probabilities.
    with open(os.path.join(directory, "cond_word_probs.txt")) as f:
      for line in f:
        word, prob = line.split(" ")
        self.cond_word_probs[word] = float(prob.strip())

  def get_tkn_probs(self, tkn, last_el):
    """ 
    Returns the conditional probabilities P(t|n)P(f1|n)... and P(t|w)P(f1|w)...
    for a single token.
    """ 
    if tkn.tkn == 'linebreak' or re.search('[0-9]', tkn.tkn):
      return (0, -100)

    # We are currently only considering names inside the same HTML element.
    # We obtained better results with a more complex approach, that considered
    # tokens accross elements, but this implementation is easier to grasp for
    # the moment.
    # TODO: this information can be incorporated in a feature.
    if last_el != None:
      if tkn.element != last_el:
        return (0, -100)

    # The total number of words and names in the corpora used to calculate the 
    # conditional probabilities loaded in load_conditional_probs(). This number
    # can vary depending on the corpora characteristics.
    num_words = 84599521 
    num_names = 3831851 

    tkn_value = tkn.tkn.strip().lower()
    prob_word = log(float(1) / (num_words + len(self.cond_word_probs)))
    if tkn_value in self.cond_word_probs:
      prob_word = self.cond_word_probs[tkn_value]
    prob_word += self.prior_probs[0]

    prob_name = log(float(1) / (num_names + len(self.cond_name_probs)))
    if tkn_value in self.cond_name_probs:
      prob_name = self.cond_name_probs[tkn_value]
    prob_name += self.prior_probs[1]

    return prob_word, prob_name

  def extract(self, tkns):
    """ 
    Assigns the most probable labels for a sliding window of tokens and
    returns the extracted names.
    """ 
    names = []

    i = 0
    while i <= len(tkns) - 4:
      cur_tkns = tkns[i:i+4]

      prob_word, prob_name = self.get_tkn_probs(cur_tkns[0], None)
      if prob_word > prob_name:
        i += 1
        continue

      last_el = cur_tkns[0].element
      name = [cur_tkns[0].tkn]
      for j in range(1, 4):
        prob_word, prob_name = self.get_tkn_probs(cur_tkns[j], last_el)
        if prob_name > prob_word:
          name.append(cur_tkns[j].tkn)          
        else:
          break
        last_el = cur_tkns[j].element

      if len(name) > 1:
        name = " ".join(name).encode('utf-8')
        if not name in names:
          names.append(name)

      i += len(name)
    return names
