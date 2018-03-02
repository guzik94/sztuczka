from setuptools import setup

import unittest
def my_test_suite():
      test_loader = unittest.TestLoader()
      test_suite = test_loader.discover('testsuite', pattern='test_*.py')
      return test_suite

setup(name='pygejm',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      test_suite='testsuite',
      author='maszynista',
      author_email='j.padukiewicz@gmail.com',
      license='',
      packages=[],
      zip_safe=False)

