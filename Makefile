all: test

test: 
	python3 -m pytest -s

install:
	python3 -m pip install -r requirements.txt

setup-ssh:
	cp .ssh/id_ecdsa ~/.ssh/id_ecdsa
	chmod 400 ~/.ssh/id_ecdsa