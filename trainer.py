class Trainer():
  def __init__(self, tokenizer):
    self.tokenizer = tokenizer
    self.probabilities = [[0] * 19, [0] * 19, [0] * 19, [0] * 19]
    self.num_4_sequences = 0
    self.unique_tkns = {}
    self.token_incidence = [[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0]]
    self.word_length = [[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0]]
    self.name_count = 0
    self.not_name_count = 0

  def mark_names(self, filename, tokens):
    correct_names = []
    with open(filename) as f:
      for line in f:
        correct_names.append([s.lower() for s in self.tokenizer.tokenize_text(line.decode("utf-8"))])

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

  def get_word_configuration_index(self, tokens):
    index = sum([2**j if tokens[::-1][j].is_name else 0 for j in range(0,4)])
    if index == 15:
      if tokens[1].is_first_name:
        index = 16
      elif tokens[2].is_first_name:
        index = 17
      elif tokens[3].is_first_name:
        index = 18
    return index

  def compare(self, x, y):
    length = self.name_count + self.not_name_count
    x = float(x[0] + x[1]) / length
    y = float(y[0] + y[1]) / length
    return -1 if y - x < 0 else 1

  def train(self, filename, correct_names_filename):
    with open(filename) as f:
      html =  f.read()

      tkns = self.tokenizer.tokenize(html)
      self.mark_names(correct_names_filename, tkns)

      i = 0
      while i <= len(tkns) - 4:
        cur_tkns = tkns[i:i+4]
        index = self.get_word_configuration_index(cur_tkns)
        num_repeated_elements = self.tokenizer.get_num_repeated_elements(cur_tkns)
        self.probabilities[num_repeated_elements][index] += 1
        self.num_4_sequences += 1
        i += 1

      for t in tkns:
        if not t.tkn in self.unique_tkns:
          self.unique_tkns[t.tkn] = [0, 0]

        word_length = len(t.tkn) if len(t.tkn) < 10 else 9
        if t.is_name:
          self.name_count += 1
          self.unique_tkns[t.tkn][1] += 1
          self.word_length[word_length][1] += 1
        else:
          self.not_name_count += 1
          self.unique_tkns[t.tkn][0] += 1
          self.word_length[word_length][0] += 1

      sorted_keys = sorted(self.unique_tkns, cmp=self.compare, key=self.unique_tkns.get)
      chunk_size = len(self.unique_tkns) / 10
      for i in range(0, 10):
        start = i * chunk_size
        end = i * chunk_size + chunk_size
        if i == 9:
          end = len(sorted_keys)

        for key in sorted_keys[start:end]: 
          self.token_incidence[i][0] += self.unique_tkns[key][0]
          self.token_incidence[i][1] += self.unique_tkns[key][1]
          self.unique_tkns[key] = i

      self.unique_tkns = {}

  def compute_probabilities(self):
    arr = [
      'WWWW', 'WWWN', 'WWNW', 'WWNN', 'WNWW', 'WNWN', 'WNNW', 'WNNN', 
      'NWWW', 'NWWN', 'NWNW', 'NWNN', 'NNWW', 'NNWN', 'NNNW', 'NNNN',
      'Nnnn', 'NNnn', 'NNNn'
    ]
    for i in range(0, 4):
      print i
      for j in range(0, 19):
        self.probabilities[i][j] = log((float(self.probabilities[i][j]) + 1) / (self.num_4_sequences + 76))
        print arr[j], self.probabilities[i][j]

    print 'Token incidence'
    for i in range(0, 10):
      self.token_incidence[i][0] = log(float(self.token_incidence[i][0] + 1) / (self.not_name_count + 10))
      self.token_incidence[i][1] = log(float(self.token_incidence[i][1] + 1) / (self.name_count + 10))
      print 'wTI' + str(i), self.token_incidence[i][0]
      print 'nTI' + str(i), self.token_incidence[i][1]

    print 'Word length'
    for i in range(1, 10):
      self.word_length[i][0] = log(float(self.word_length[i][0] + 1) / (self.not_name_count + 10))
      self.word_length[i][1] = log(float(self.word_length[i][1] + 1) / (self.name_count + 10))
      print 'wWL' + str(i), self.word_length[i][0]
      print 'nWL' + str(i), self.word_length[i][1]
