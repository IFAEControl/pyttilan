__author__ = 'droman'

from setuptools import find_packages, setup

setup(name="pytticpx",
        version="0.0.1",
        description="Library to communicate with TTi CPX power supply",
        author="David Roman",
        author_email="droman@ifae.es",
        platforms=["any"],
        license="BSD",
        packages=find_packages(),
        )
