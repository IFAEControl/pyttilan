#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

# Read README and CHANGES files for the long description
here = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'README.txt')).read()
PACKAGEFULLNAME = 'pytticpx'
PACKAGENAME = 'pytticpx'
DESCRIPTION = 'Library to control remotely a TTi CPX Power Supply'
LONG_DESCRIPTION = ''
AUTHOR = 'David Roman'
AUTHOR_EMAIL = 'droman@ifae.es'
LICENSE = open(os.path.join(here, 'LICENSE')).read()
URL = "https://gitlab.pic.es/ifaecontrol/pytticpx"
VERSION = '0.1.2'
RELEASE = 'dev' not in VERSION

print(find_packages('pytticpx'))
# Read the version information
#execfile(os.path.join(here, '__init__.py'))
setup(
      name=PACKAGEFULLNAME,
      version=VERSION,
      description=DESCRIPTION,
      #scripts=scripts,
      requires=[],
      install_requires=[],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,
      classifiers=[
                   "Development Status :: 4 - Beta",
                   "Programming Language :: Python",
                  ],
      #ata=True,
      packages=find_packages()
    #zip_safe=True,
)

# from distutils.core import setup
#
# setup(
#             name="pytticpx",
#             packages=['pytticpx'],
#             version="0.1.1",
#             description="Library to communicate with TTi CPX power supply",
#             author="David Roman",
#             author_email="droman@ifae.es",
#             url='https://gitlab.pic.es/ifaecontrol/pytticpx',
#         )
