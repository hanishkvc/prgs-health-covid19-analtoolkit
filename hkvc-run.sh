#!/bin/bash
# Helper script for managing related stuff
# v20200419IST1644, HanishKVC

function setup_python_modules() {

	#ln -s ../../../../../../Libs/python/xmlparser/xmlparser.py xmlparser.py
	git submodule add https://github.com/hanishkvc/libs-python-xmlparser.git libs/xmlparser

}

function cleanup() {

	rm -rf __pycache__
	rm -rf libs/xmlparser/__pycache__

}

$@

