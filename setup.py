#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = 'apibean-dev',
  version = '0.0.1-alpha02',
  description = 'apibean development module',
  author = 'skelethon',
  license = 'GPL-3.0',
  url = 'https://github.com/skelethon/apibean-dev',
  download_url = 'https://github.com/skelethon/apibean-dev/downloads',
  keywords = ['apibean'],
  classifiers = [],
  install_requires = open("requirements.txt").readlines(),
  python_requires=">=3.7",
  package_dir = {'':'src'},
  packages = setuptools.find_packages('src'),
)
