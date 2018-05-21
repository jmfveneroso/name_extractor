# coding=UTF-8

import os
import re
from math import log

class ComplexExtractor():
  """ 
  The extractor class extracts names from a list of tokens based on
  the most likely sequence of labels on a sliding window given
  the prior and conditional probabilities.
  """

  def __init__(self):
    # The conditional name P(t|N) and word probabilities P(t|W) were estimated 
    # offline through maximum likelihood over two corpora containing only names 
    # and only words, respectively.
    self.cond_name_probs = {}
    self.cond_word_probs = {}

    # Prior probabilities for each one of these sequences will be estimated 
    # from the test data. This is the only possible source of overfitting.
    # The possible label sequences for a window of size 4 are (W=word, N=name):
    # WWWW, WWWN, WWNW, WWNN, WNWW, WNWN, WNNW, WNNN, 
    # NWWW, NWWN, NWNW, NWNN, NNWW, NNWN, NNNW, NNNN
    # Consider that the corresponding index for a given sequence is the binary
    # number obtained when W=0 and N=1. For example: WWNN == 0011, so its index
    # is 3.
    self.prior_probs = [0] * 16

    # Feature probabilities will be calculated on a second run over the
    # token list. Only structural features are being currently used.
    self.feature_probs = [{}, {}, {}, {}, {}]

    # Load the conditional probabilities from a file.
    self.load_conditional_probs()

  def laplace_smoothing(self, count, total_count, possibilities):
    """ 
    Returns a smoothed probability through the Laplace or Additive Smoothing 
    method. More information here: 
    https://en.wikipedia.org/wiki/Additive_smoothing
    """
    return float(count + 1) / (total_count + possibilities)

  def get_sequence_index(self, seq):
    """ 
    Get the sequence index in the prior probabilities array. The index of a 
    given sequence of labels is the binary number obtained when word=0 and name=1. 
    For example: WWNN == 0011, so the index is 3.
    """
    return sum([2**j if seq[::-1][j].is_name else 0 for j in range(0, 4)])

  def fit(self, docs):
    """ 
    Estimates the prior probabilities from a list of test documents.
    """
    if len(docs) == 0:
      self.load_prior_probs()
      return

    self.prior_probs = [0] * 16
    num_seqs = 0

    for doc in docs:
      i = 0
      tkns = doc[1]
      while i <= len(tkns) - 4:
        index = self.get_sequence_index(tkns[i:i+4])
        self.prior_probs[index] += 1
        num_seqs += 1
        i += 1

    # Compute prior probabilities.
    for i in range(0, 16):
      self.prior_probs[i] = log(self.laplace_smoothing(
        self.prior_probs[i], num_seqs, 16
      ))

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

  def load_prior_probs(self, directory = "../probabilities"):
    """ 
    Loads prior probabilities P(yyyy) from a file. 
    """
    with open(os.path.join(directory, "prior_probs.txt")) as f:
      for i in range(0, 16):
        prob = f.readline().split(" ")[1]
        self.prior_probs[i] = float(prob.strip())

  def get_tkn_probs(self, tkn, last_el, use_structural_features):
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

    prob_name = log(float(1) / (num_names + len(self.cond_name_probs)))
    if tkn_value in self.cond_name_probs:
      prob_name = self.cond_name_probs[tkn_value]

    # Structural features are features derived from the HTML structure.
    if use_structural_features:
      for i in range(0, len(self.feature_probs)):
        key = tkn.structural_features[i]
        if key in self.feature_probs[i]:
          prob_word += self.feature_probs[i][key][0]
          prob_name += self.feature_probs[i][key][1]

    return prob_word, prob_name

  def get_sequence_probs(self, tkns, use_structural_features):
    """ 
    Returns the probabilities of the 16 possible label sequences 
    for a sequence of tokens. That is: P(yyyy)P(t1|y)P(t2|y)P(t3|y)P(t4|y), where
    y is a label (word or name).
    """ 
    last_el = None
    tkn_probs = []
    for tkn in tkns:
      tkn_probs.append(self.get_tkn_probs(tkn, last_el, use_structural_features))
      last_el = tkn.element

    sequence_probs = [0] * 16
    for i in range(0, 16):
      selector_array = [1 if ((i & 2**j) == 2**j) else 0 for j in reversed(range(0, 4))] 
      for j in range(0, len(tkns)):
        sequence_probs[i] += tkn_probs[j][selector_array[j]]
      sequence_probs[i] += self.prior_probs[i]
    return sequence_probs

  def estimate_structural_features(self, tkns):
    """ 
    Estimates the probabilities associated with a structural feature
    by a maximum likelihood estimation obtained after the extractor has
    already assigned provisional labels to the list of tokens.
    """ 
    # We store the feature counts here.
    self.feature_probs = [{}, {}, {}, {}, {}] 

    name_count, word_count = 0, 0
    for tkn in tkns:
      if tkn.is_name:
        name_count += 1
      else:
        word_count += 1

      for i in range(0, len(tkn.structural_features)):
        feature_val = tkn.structural_features[i]
        if not feature_val in self.feature_probs[i]:
          self.feature_probs[i][feature_val] = [0, 0]
        self.feature_probs[i][feature_val][1 if tkn.is_name else 0] += 1

    for i in range(0, len(tkn.structural_features)):
      for key in self.feature_probs[i]:
        self.feature_probs[i][key][0] = log(self.laplace_smoothing(
          self.feature_probs[i][key][0], word_count, len(self.feature_probs[i])
        ))
        self.feature_probs[i][key][1] = log(self.laplace_smoothing(
          self.feature_probs[i][key][1], name_count, len(self.feature_probs[i])
        ))

  def assign_labels(self, tkns, use_structural_features):
    """ 
    Assigns the most probable labels for a sliding window of tokens and
    returns the extracted names.
    """ 
    names = []

    i = 0
    while i <= len(tkns) - 4:
      cur_tkns = tkns[i:i+4]

      # Get the sequence of labels with maximum probability.
      seq_probs = self.get_sequence_probs(cur_tkns, use_structural_features)
      index = seq_probs.index(max(seq_probs))

      # In sequences: WWWW, WWWN, WWNW, WWNN, WNWW, WNWN, WNNW, WNNN, 
      # NWWW, NWWN, NWNW, NWNN - the first token is a word or, the first
      # token is a name but the second token is a word. Since we don't
      # want single names we will discard those as words and slide the window
      # by one token.
      if index < 12:
        tkns[i].is_name = False
        i += 1

      # At least the two first tokens are names. These are the sequences:
      # NNWW, NNWN, NNNW, NNNN.
      else:
        name_length = 2 if (index - 12 == 0) else index - 11

        if name_length > len(cur_tkns):
          name_length = len(cur_tkns)

        name_start = int(i)
        name_end = int(i) + int(name_length)
        name_tkns = tkns[name_start:name_end]

        for tkn in name_tkns:
          tkn.is_name = True

        # Slide window by the name length.
        i += name_length
        if len(name_tkns) <= 1:
          continue

        name_tkns = [t.tkn for t in name_tkns]
        if len([t for t in name_tkns if len(t) > 1]) == 0:
          continue

        # Only add unique names.
        name = " ".join(name_tkns).encode('utf-8')
        if not name in names:
          names.append(name)
    return names

  def extract(self, tkns):
    """ 
    Extracts names from a list of tokens.
    """ 
    self.feature_probs = [{}, {}, {}, {}, {}]
    names = self.assign_labels(tkns, False)
    for i in range(0, 2): 
      self.estimate_structural_features(tkns)
      names = self.assign_labels(tkns, True)
    return names
