
# Which version of python are we using?
ifndef python
python=3.2
endif

# Which devices are connected and configured for loopback testing?
ifndef devices
devices=mcp23017 gpio mcp23008
endif


ARCHITECTURE:=$(shell uname -m)

PYTHON_ENV=$(PWD)/python$(python)-$(ARCHITECTURE)
PYTHON_EXE=$(PYTHON_ENV)/bin/python
PIP=$(PYTHON_EXE) $(PYTHON_ENV)/bin/pip

PROJECT:=$(shell $(PYTHON_EXE) setup.py --name)
VERSION:=$(shell $(PYTHON_EXE) setup.py --version)

EXAMPLES:=$(wildcard examples/*)
EXAMPLE_DOCS:=$(EXAMPLES:%=docs/%.html)

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
	$(PIP) install -r requirements.txt
.PHONY: env-libs

env-clean:
	rm -rf $(PYTHON_ENV)/
.PHONY: env-clean

env-again: env-clean env
.PHONY: env-again

check:
	$(PYTHON_EXE) setup.py test
.PHONY: check

check-install: TESTENV=$(abspath build/test-python$(python)-$(ARCHITECTURE))
check-install: dist
	$(MAKE) PYTHON_ENV=$(TESTENV) env-again
	mkdir -p build/
	cd build/ && tar xzf ../dist/$(PROJECT)-$(VERSION).tar.gz
	cd build/$(PROJECT)-$(VERSION) && $(TESTENV)/bin/python setup.py install
	$(TESTENV)/bin/python setup.py test
.PHONY: check-install

README.rst: README.md
	pandoc --output=$@ $<

dist/$(PROJECT)-$(VERSION).tar.gz: setup.py Makefile README.rst
	$(PYTHON_EXE) setup.py sdist

dist: dist/$(PROJECT)-$(VERSION).tar.gz
.PHONY: dist

docs: $(EXAMPLE_DOCS) docs/examples/code-guide.css
.PHONY: docs

docs/examples/%.html: examples/%
	@mkdir -p $(dir $@)
	code-guide $< -o $@ -r . -l python -c "#" -t '(.+)' '\1.html'

docs/examples/code-guide.css:
	@mkdir -p $(dir $@)
	code-guide --extract-resources --resource-dir=$(dir $@)

clean:
	rm -rf output/ dist/ build/ docs/ MANIFEST README.rst quick2wire_api.egg-info README.rst
	find . -name '*.pyc' -o -name '*~' | xargs -r rm -f
.PHONY: clean

again: clean all
.PHONY: again


SCANNED_FILES=$(shell find src/ -type d) $(shell find test/ -type d) Makefile setup.py

.PHONY: continually
continually:
	@while true; do \
	  clear; \
	  if not make check; \
	  then \
	      notify-send --icon=error --category=build --expire-time=250 "$(PROJECT) build broken"; \
	  fi; \
	  date; \
	  inotifywait -r -qq -e modify -e delete $(SCANNED_FILES); \
	done
