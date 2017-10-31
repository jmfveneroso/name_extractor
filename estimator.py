import re
from math import log

class Estimator():
  def __init__(self, tokenizer):
    self.tokenizer = tokenizer
    self.conditional_probabilities = [[0] * 19, [0] * 19, [0] * 19, [0] * 19]
    self.name_cond_probs = {}
    self.word_cond_probs = {}
    self.token_incidence = [[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0]]
    self.word_length = [[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0]]
    self.unique_tkns = {}

    self.first_parents = {}
    self.second_parents = {}
    self.third_parents = {}
    self.element_positions = {}
    self.class_names = {}
    self.child_pos_ = {}

  def load_name_cond_probs(self, filename):
    with open(filename) as f:
      for line in f:
        word, prob = line.split(" ")
        self.name_cond_probs[word] = float(prob.strip())

  def load_word_cond_probs(self, filename):
    with open(filename) as f:
      for line in f:
        word, prob = line.split(" ")
        self.word_cond_probs[word] = float(prob.strip())

  def load_conditional_probabilities(self, filename):
    with open(filename) as f:
      for i in range(0, 4):
        f.readline()
        for j in range(0, 19):
          self.conditional_probabilities[i][j] = float(f.readline().split(" ")[1])
      f.readline()
      for i in range(0, 10):
        for j in range(0, 2):
          self.token_incidence[i][j] = float(f.readline().split(" ")[1])
      f.readline()
      for i in range(0, 9):
        for j in range(0, 2):
          self.word_length[i + 1][j] = float(f.readline().split(" ")[1])

  def calculate_tkn_incidence(self, tkns):
    self.unique_tkns = {}
    for tkn in tkns:
      if not tkn.tkn in self.unique_tkns:
        self.unique_tkns[tkn.tkn] = 0
      self.unique_tkns[tkn.tkn] += 1

    sorted_keys = sorted(self.unique_tkns, key=self.unique_tkns.get, reverse=True)
    chunk_size = len(self.unique_tkns) / 10
    for i in range(0, 10):
      start = i * chunk_size
      end = i * chunk_size + chunk_size
      if i == 9:
        end = len(sorted_keys)

      for key in sorted_keys[start:end]: 
        self.unique_tkns[key] = i


  def get_tkn_probs(self, tkn, last_el, second_passing):
    if tkn.tkn == 'linebreak' or re.search('[0-9]', tkn.tkn):
      return (0, -100)

    if last_el != None:
      if tkn.element != last_el and tkn.element != last_el.parent and tkn.element.parent != last_el and tkn.element.parent != last_el.parent:
        return (0, -100)

    tkn_value = tkn.tkn.strip().lower()
    prob_word = log(float(1) / (84599521 + len(self.word_cond_probs)))
    if tkn_value in self.word_cond_probs:
      prob_word = self.word_cond_probs[tkn_value]

    prob_name = log(float(1) / (3831851 + len(self.name_cond_probs)))
    if tkn_value in self.name_cond_probs:
      prob_name = self.name_cond_probs[tkn_value]

    incidence = self.unique_tkns[tkn_value]
    prob_word += self.token_incidence[incidence][0]
    prob_name += self.token_incidence[incidence][1]

    # Token length.
    length = len(tkn_value) if len(tkn_value) < 9 else 9
    prob_word += self.word_length[length][0]
    prob_name += self.word_length[length][1]

    if second_passing:
      prob_word += self.first_parents[tkn.parent][0]
      # prob_word += self.second_parents[tkn.second_parent][0]
      prob_word += self.third_parents[tkn.third_parent][0]
      prob_word += self.class_names[tkn.class_name][0]
      # prob_word += self.child_pos_[tkn.text_depth][0]
      prob_word += self.element_positions[tkn.element_position][0]
      prob_name += self.first_parents[tkn.parent][1]
      # prob_name += self.second_parents[tkn.second_parent][1]
      prob_name += self.third_parents[tkn.third_parent][1]
      prob_name += self.class_names[tkn.class_name][1]
      # prob_name += self.child_pos_[tkn.text_depth][1]
      prob_name += self.element_positions[tkn.element_position][1]

    return prob_word, prob_name

  def get_full_probs(self, tkns, second_passing):
    num_repeated_elements = self.tokenizer.get_num_repeated_elements(tkns)

    last_el = None
    tkn_probs = []
    for tkn in tkns:
      tkn_probs.append(self.get_tkn_probs(tkn, last_el, second_passing))
      last_el = tkn.element

    full_probs = [0] * 19
    for i in range(0, 16):
      selector_array = [1 if ((i & 2**j) == 2**j) else 0 for j in reversed(range(0,4))] 
      for j in range(0, len(tkns)):
        full_probs[i] += tkn_probs[j][selector_array[j]]
        if i == 15:
          full_probs[16] += tkn_probs[j][selector_array[j]]
          full_probs[17] += tkn_probs[j][selector_array[j]]
          full_probs[18] += tkn_probs[j][selector_array[j]]

      full_probs[i] += self.conditional_probabilities[num_repeated_elements][i]
      if i == 15:
        full_probs[16] += self.conditional_probabilities[num_repeated_elements][16]
        full_probs[17] += self.conditional_probabilities[num_repeated_elements][17]
        full_probs[18] += self.conditional_probabilities[num_repeated_elements][18]

    arr = [
      'WWWW', 'WWWN', 'WWNW', 'WWNN', 'WNWW', 'WNWN', 'WNNW', 'WNNN', 
      'NWWW', 'NWWN', 'NWNW', 'NWNN', 'NNWW', 'NNWN', 'NNNW', 'NNNN',
      'Nnnn', 'NNnn', 'NNNn'
    ]
    # probs = [arr[j] + str(self.conditional_probabilities[num_repeated_elements][j]) for j in range(0,18)]
    probs = [arr[j] + str(full_probs[j]) for j in range(0,19)]
    # print [t.tkn for t in tkns], tkn_probs, self.conditional_probabilities[num_repeated_elements]
    # if verbose:
    #   print [t.tkn for t in tkns], num_repeated_elements, max(full_probs), probs, tkn_probs
    return full_probs

  def calculate_secondary_features(self, tkns):
    self.first_parents = {}
    self.second_parents = {}
    self.third_parents = {}
    self.class_names = {}
    self.child_pos_ = {}
    self.element_positions = {}
    name_count = 0
    not_name_count = 0

    for tkn in tkns:
      index = 1 if tkn.is_name else 0
      if tkn.is_name:
        name_count += 1
      else:
        not_name_count += 1

      if not tkn.parent in self.first_parents:
        self.first_parents[tkn.parent] = [0, 0]
      if not tkn.second_parent in self.second_parents:
        self.second_parents[tkn.second_parent] = [0, 0]
      if not tkn.third_parent in self.third_parents:
        self.third_parents[tkn.third_parent] = [0, 0]
      if not tkn.class_name in self.class_names:
        self.class_names[tkn.class_name] = [0, 0]
      if not tkn.text_depth in self.child_pos_:
        self.child_pos_[tkn.text_depth] = [0, 0]
      if not tkn.element_position in self.element_positions:
        self.element_positions[tkn.element_position] = [0, 0]

      self.first_parents[tkn.parent][index] += 1
      self.second_parents[tkn.second_parent][index] += 1
      self.third_parents[tkn.third_parent][index] += 1
      self.class_names[tkn.class_name][index] += 1
      self.child_pos_[tkn.text_depth][index] += 1
      self.element_positions[tkn.element_position][index] += 1

    for key in self.first_parents:
      self.first_parents[key][0] = log(float(self.first_parents[key][0] + 1) / (not_name_count + len(self.first_parents)))
      self.first_parents[key][1] = log(float(self.first_parents[key][1] + 1) / (name_count + len(self.first_parents)))
    for key in self.second_parents:
      self.second_parents[key][0] = log(float(self.second_parents[key][0] + 1) / (not_name_count + len(self.second_parents)))
      self.second_parents[key][1] = log(float(self.second_parents[key][1] + 1) / (name_count + len(self.second_parents)))
    for key in self.third_parents:
      self.third_parents[key][0] = log(float(self.third_parents[key][0] + 1) / (not_name_count + len(self.third_parents)))
      self.third_parents[key][1] = log(float(self.third_parents[key][1] + 1) / (name_count + len(self.third_parents)))
    for key in self.class_names:
      self.class_names[key][0] = log(float(self.class_names[key][0] + 1) / (not_name_count + len(self.class_names)))
      self.class_names[key][1] = log(float(self.class_names[key][1] + 1) / (name_count + len(self.class_names)))
    for key in self.child_pos_:
      self.child_pos_[key][0] = log(float(self.child_pos_[key][0] + 1) / (not_name_count + len(self.child_pos_)))
      self.child_pos_[key][1] = log(float(self.child_pos_[key][1] + 1) / (name_count + len(self.child_pos_)))
    for key in self.element_positions:
      self.element_positions[key][0] = log(float(self.element_positions[key][0] + 1) / (not_name_count + len(self.element_positions)))
      self.element_positions[key][1] = log(float(self.element_positions[key][1] + 1) / (name_count + len(self.element_positions)))
