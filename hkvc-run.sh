#!/bin/bash
# Helper script for managing related stuff
# v20200520IST1644, HanishKVC

function dev_setup_git_submodules() {

	#ln -s ../../../../../../Libs/python/xmlparser/xmlparser.py xmlparser.py
	git submodule add https://github.com/hanishkvc/libs-python-xmlparser.git libs/xmlparser
	git submodule add https://github.com/hanishkvc/prgs-libreoffice-pyuno_toolkit.git libs/hkvc_pyuno_toolkit

}

function get_git_submodules() {

	git submodule update --init --recursive

}

function update_git_submodules() {

	git submodule update --remote

}

function cleanup() {

	rm -rf __pycache__
	rm -rf libs/xmlparser/__pycache__

}

function test_run_10() {

	rm -f /tmp/*png /tmp/*jpg
	#./hkvc-covid19-analtoolkit.py --sel EUWorld IN IE UK AE CA US RU BR --sel Cov19In KL KA DL MH MP BR
	./hkvc-covid19-analtoolkit.py --no_scalediff
	convert /tmp/*png /tmp/1.jpg
	./hkvc-covid19-analtoolkit.py
	convert /tmp/*png /tmp/2.jpg

}

function test_run_11() {

	./hkvc-covid19-analtoolkit.py --test_mixmatch

}

function test_run() {

	sDate=`date +%Y%m%d`
	./hkvc-covid19-analtoolkit.py
	./hkvc-covid19-analtoolkit.py --plotsel_partial
	./hkvc-covid19-analtoolkit.py --cov19in data/Cov19In-$sDate-confirmed.csv --euworld data/EUWorld-$sDate.csv --sel EUWorld IN IE UK AE CA US RU BR --sel Cov19In KL KA DL MH GJ MP BR

}

function _ctags() {

	ctags *py

}

$@

