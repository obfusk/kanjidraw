SHELL   := /bin/bash
PYTHON  ?= python3
VERBOSE ?= --verbose

export PYTHONWARNINGS := default

.PHONY: all test clean cleanup install

all:

test:
	$(PYTHON) -m kanjidraw.gui $(VERBOSE) --doctest
	$(PYTHON) -m kanjidraw.lib $(VERBOSE) --doctest

clean: cleanup
	rm -fr kanjidraw.egg-info/

cleanup:
	find -name '*~' -delete -print
	rm -fr kanjidraw/__pycache__/
	rm -fr build/ dist/
	rm -fr .coverage htmlcov/

install:
	$(PYTHON) -mpip install -e .

.PHONY: _package _publish

_package:
	$(PYTHON) setup.py sdist bdist_wheel
	twine check dist/*

_publish: cleanup _package
	read -r -p "Are you sure? "; \
	[[ "$$REPLY" == [Yy]* ]] && twine upload dist/*
