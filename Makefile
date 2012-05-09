
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

all: check dist
.PHONY: all

env: env-base env-libs
.PHONY: env

env-base:
	mkdir -p $(dir $(PYTHON_ENV))
	tools/virtualenv --python=python$(python) $(PYTHON_ENV)
	rm -f distribute-*.tar.gz
.PHONY: env-base

env-libs:
	$(PIP) install pytest
.PHONY: env-libs

env-clean:
	rm -rf $(PYTHON_ENV)/
.PHONY: env-clean

env-again: env-clean env
.PHONY: env-again

check:
	PYTHONPATH=src:$(PYTHON_LIBDIR) $(PYTHON_ENV)/bin/py.test test
.PHONY: check

check-install:
	$(MAKE) PYTHON_ENV=build/test-$(python)-$(ARCHITECTURE) env-again
	build/test-$(python)-$(ARCHITECTURE)/bin/python$(python) setup.py install
	$(MAKE) PYTHON_ENV=build/test-$(python)-$(ARCHITECTURE) check
.PHONY: check-install

build/test-$(python)-$(ARCHITECTURE):
	mkdir -p $(dir $@)
	cp -R $(PYTHON_ENV) $@

dist/$(PROJECT)-$(VERSION).tar.gz: setup.py Makefile README.rst
	$(PYTHON_EXE) setup.py sdist

README.rst: README.md
	pandoc --from=markdown --to=rst $^ > $@

dist: dist/$(PROJECT)-$(VERSION).tar.gz
.PHONY: dist

clean:
	rm -rf output/ dist/ build/ MANIFEST README.rst
	find . -name '*.pyc' -o -name '*~' | xargs -r rm
.PHONY: clean

again: clean all
.PHONY: again
