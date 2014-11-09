
.PHONY: default test

default: test

test:
	python ./transaction_charts.py

open:
	open ./test.html
