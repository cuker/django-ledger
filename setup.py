#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.0.1'
LONG_DESC = """\

"""

setup(name='django-ledger',
      version=VERSION,
      description="A simple library for creating a double ledger system",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='django accounting ledger',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://github.com/cuker/django-ledger',
      license='New BSD License',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      zip_safe=True,
      install_requires=[
      ],
      test_suite='tests.runtests.runtests',
      )
