#!/usr/bin/env python

from distutils.core import setup

setup(name='funklib',
      version='0.5',
      description='Utility modules for functional programming',
      author='drpyser',
      author_email='schok53@gmail.com',
      url='https://github.com/DrPyser/funklib',
      packages=['funklib', 'multimethods', 'datatypes', 'core'],
     )
