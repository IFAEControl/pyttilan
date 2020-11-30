#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

# Read README and CHANGES files for the long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as fh:
      long_description = fh.read()

print(find_packages(exclude=('tests',)))
setup(
      name="pyttilan",
      version="0.2.1",
      description="Library to control TTi Power Supplies over network",
      long_description_content_type="text/markdown",
      long_description=long_description,
      requires=[],
      install_requires=[],
      provides=["pyttilan"],
      author="David Roman, Otger Ballester",
      author_email="ifae-control@ifae.es",
      license="CC0 1.0 Universal",
      url="https://github.com/IFAEControl/pyttilan",
      zip_safe=False,
      classifiers=[
                   "Development Status :: 4 - Beta",
                   "Programming Language :: Python :: 3",
                  ],
      package_dir={'': 'src'},
      packages=find_packages(where=os.path.join('.', 'src'), exclude=('tests',))
)
