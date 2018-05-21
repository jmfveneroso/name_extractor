# coding=UTF-8

import abc

class Extractor(abc.ABC):
  @abc.abstractmethod
  def fit(self, docs):
    pass

  @abc.abstractmethod
  def extract(self, tkns):
    pass
