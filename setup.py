#!/usr/bin/env python

import os
from distutils.core import setup

def contents_of(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return 'Quick2Wire API'


setup(name='Quick2Wire',
      version='1.1.0.0-a',
      description='Quick2Wire API',
      long_description=contents_of('README.rst'),
      author='Quick2Wire Ltd.',
      author_email='info@quick2wire.com',
      url='http://quick2wire.com',
      
      license="LGPL or MIT",
      
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License (LGPL)',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Topic :: Software Development',
      ],
      platforms=['Linux'],
      
      provides=['quick2wire.gpio', 'quick2wire.i2c'],
      packages=['quick2wire'],
      package_dir = {'': 'src'},
      scripts=[],
      
      requires=[]
)

