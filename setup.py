# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

setup(
  name='name_extractor',
  version='0.1.0',
  description='Statistical name extractor for HTML.',
  long_description=readme,
  author='João Mateus de Freitas Veneroso',
  author_email='jmfveneroso@gmail.com',
  url='https://github.com/jmfveneroso/name_extractor',
  license=license,
  packages=find_packages(exclude=('tests', 'dataset', 'conditional_dataset', 'tex', 'deprecated'))
)
