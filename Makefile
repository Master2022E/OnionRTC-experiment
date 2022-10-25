all: test

test: install
	python -m pytest -s

install:
	python -m pip install -r requirements.txt

