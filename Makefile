all: test

test: 
	python3 -m pytest -s

install:
	python3 -m pip install -r requirements.txt

setup-ssh:
	cp ./ssh ~ -r
	chmod 400 ~/.ssh/id_ecdsa