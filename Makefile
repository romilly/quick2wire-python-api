
# Which version of python are we using?
ifndef python
python=3.1
endif

ARCHITECTURE:=$(shell uname -m)

PYTHON_ENV=$(PWD)/python$(python)-$(ARCHITECTURE)
PYTHON_BUILDDIR=$(PYTHON_ENV)/build
PYTHON_LIBDIR=$(PYTHON_ENV)/lib/python$(python)/site-packages

# To stop setup.py complaining about paths
export PYTHONPATH=$(PYTHON_LIBDIR)

PROJECT=quick2wire-python-api
PROJECT_VER:=0.0.1.0

all: check
.PHONY: all

env: env-base env-libs
.PHONY: env

env-libs:
	$(PYTHON_ENV)/bin/pip install pytest
.PHONY: env-libs

env-base:
	lib-src/virtualenv --python=python$(python) $(PYTHON_ENV)
.PHONY: env-base

env-clean:
	rm -rf $(PYTHON_ENV)/
.PHONY: env-clean

env-again: env-clean env
.PHONY: env-again

check:
	PYTHONPATH=src:$(PYTHON_LIBDIR) $(PYTHON_ENV)/bin/py.test test
.PHONY: check

SCANNED_FILES=src tests Makefile setup.py bin

clean:
	rm -rf output/
	find . -name '*.pyc' | xargs rm
	find . -name '*~' | xargs rm
.PHONY: clean

again: clean all
.PHONY: again
