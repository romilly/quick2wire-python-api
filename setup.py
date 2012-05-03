#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='Quick2Wire',
      version='0.0.0.1',
      description='Quick2Wire API',
      long_description=read("README.rst"),
      author='Quick2Wire Ltd.',
      author_email='info@quick2wire.com',
      url='http://quick2wire.com',
      
      license="LGPL or MIT",
      
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Lesser GNU General Public License (LGPL)',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Topic :: Software Development',
      ],
      platforms=['Linux'],
      
      provides=['quick2wire.gpio'],
      packages=['quick2wire'],
      package_dir = {'': 'src'},
      scripts=[],
      
      requires=[]
)

