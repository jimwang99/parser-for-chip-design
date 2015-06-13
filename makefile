SHELL=/usr/bin/tcsh -f

debug:
	python2.7 spice_netlist_parser.py
# 	python2.7 verilog_netlist_parser.py


test:
	python2.7 test.py

.PHONY: debug test
