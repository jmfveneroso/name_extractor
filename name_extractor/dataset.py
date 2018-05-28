# coding=UTF-8

import os
import errno
import tokenizer

class Dataset():
  tokenizer = tokenizer.Tokenizer()
  directory = "../dataset"
  def __init__(self):
    self.documents = []
 
  def load(self):
    urls_file = os.path.join(Dataset.directory, 'urls.txt')

    if not os.path.isfile(urls_file):
      raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), urls_file
      )

    with open(urls_file) as f:
      counter = 1
      for url in f:
        # if counter > 5: return
        file_num = str(counter).zfill(3)

        html_page_file = os.path.join(Dataset.directory, 'html_pages/%s.html' % file_num)
        if not os.path.isfile(html_page_file):
          raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), html_page_file
          )

        target_names_file = os.path.join(Dataset.directory, 'target_names/target_names_%s.txt' % file_num)
        if not os.path.isfile(target_names_file):
          raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), target_names_file
          )

        target_names = []
        with open(target_names_file) as f:
          for name in f:
            name = " ".join(Dataset.tokenizer.tokenize_text(name.decode("utf-8").strip()))
            target_names.append(name.strip())

        with open(html_page_file) as f:
          html = f.read()

        # Add document tuple with the format: (url, tokens, target_names).
        self.documents.append((url.strip(), html, target_names))
        counter += 1

  def get_document(self, doc_num):
    urls_file = os.path.join(Dataset.directory, 'urls.txt')

    if not os.path.isfile(urls_file):
      raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), urls_file
      )

    url = ''
    with open(urls_file) as f:
      counter = 1
      for line in f:
        if counter == doc_num:
          url = line.strip()
          break
        counter += 1

    doc_num = str(doc_num).zfill(3)

    html_page_file = os.path.join(Dataset.directory, 'html_pages/%s.html' % doc_num)
    if not os.path.isfile(html_page_file):
      raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), html_page_file
      )

    target_names_file = os.path.join(Dataset.directory, 'target_names/target_names_%s.txt' % doc_num)
    if not os.path.isfile(target_names_file):
      raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), target_names_file
      )

    target_names = []
    with open(target_names_file) as f:
      for name in f:
        name = " ".join(Dataset.tokenizer.tokenize_text(name.decode("utf-8").strip()))
        target_names.append(name.strip())

    with open(html_page_file) as f:
      html = f.read()

    return (url.strip(), html, target_names)
