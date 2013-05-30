#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys
import os
import subprocess

package = 'quick2wire'


def contents_of(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return 'Quick2Wire API'


def devices():
    return os.environ.get('devices','').split()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = [package,
                          '--duration=5', 
                          '-m', 
                          ("").join(d + " or " for d in devices()) + "not loopback"]
    
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name='quick2wire-api',
      version="0.0.0.2",
      description='Quick2Wire API for Physical Computing',
      long_description=contents_of('README.txt'),
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
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Software Development',
      ],
      platforms=['Linux'],
      
      provides=[package],
      
      packages=[package, package+'.parts'],
      scripts=[],
      
      tests_require=['pytest==2.3.4', 'factcheck==1.1.0.0'],
      cmdclass = {'test': PyTest}
)

