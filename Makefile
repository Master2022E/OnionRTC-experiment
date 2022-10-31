all: test

test: 
	python3 -m pytest -s

install:
	python3 -m pip install -r requirements.txt

