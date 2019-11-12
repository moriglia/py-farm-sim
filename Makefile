TEST_DIR ?= test
test_targets = $(patsubst $(TEST_DIR)/%.py,%,$(shell ls $(TEST_DIR)/test_*.py))
PACKAGE_DIR ?= pyfarmsim

F ?= $(TEST_DIR)/*.py $(PACKAGE_DIR)/*.py

.PHONY: init cleantest pylama

init:
	@pipenv install

test: $(test_targets)
test_%: $(TEST_DIR)/test_%.py
	pipenv run python3 -m unittest $< -v

cleantest:
	@rm -rf $(TEST_DIR)/__pycache__

pylama:
	@pipenv run python3 -m pylama $(F)
