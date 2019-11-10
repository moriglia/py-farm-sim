init:
	pipenv install

test:
	pipenv run python3 -m unittest discover

.PHONY: init test
