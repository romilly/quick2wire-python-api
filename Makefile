
# Which version of python are we using?
ifndef python
python=3.1
endif

ARCHITECTURE:=$(shell uname -m)

PYTHON_ENV=$(PWD)/python$(python)-$(ARCHITECTURE)
PYTHON_EXE=$(PYTHON_ENV)/bin/python
PIP=$(PYTHON_ENV)/bin/pip
PYTHON_BUILDDIR=$(PYTHON_ENV)/build
PYTHON_LIBDIR=$(PYTHON_ENV)/lib/python$(python)/site-packages

# To stop setup.py complaining about paths
export PYTHONPATH=$(PYTHON_LIBDIR)

PROJECT=quick2wire-python-api
VERSION:=$(shell $(PYTHON_EXE) setup.py --version)

all: check
.PHONY: all

env: env-base env-libs
.PHONY: env

env-libs:
	$(PIP) install pytest
.PHONY: env-libs

env-base:
	tools/virtualenv --python=python$(python) $(PYTHON_ENV)
	rm -f distribute-*.tar.gz
.PHONY: env-base

env-clean:
	rm -rf $(PYTHON_ENV)/
.PHONY: env-clean

env-again: env-clean env
.PHONY: env-again

check:
	PYTHONPATH=src:$(PYTHON_LIBDIR) $(PYTHON_ENV)/bin/py.test test
.PHONY: check


dist/$(PROJECT)-$(VERSION).tar.gz: setup.py Makefile
	$(PYTHON_EXE) setup.py sdist

dist: dist/$(PROJECT)-$(VERSION).tar.gz
.PHONY: dist

clean:
	rm -rf output/
	find . -name '*.pyc' | xargs rm
	find . -name '*~' | xargs rm
.PHONY: clean

again: clean all
.PHONY: again
