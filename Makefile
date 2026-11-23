UV := uv
SRC := src

ifneq ("$(wildcard /sgoinfre/$(USER))","")
	CACHE_BASE := /sgoinfre/$(USER)/.cache
else
	CACHE_BASE := /tmp/$(USER)-cache
endif

CACHE_ENV := UV_CACHE_DIR=$(CACHE_BASE)/uv HF_HOME=$(CACHE_BASE)/huggingface

DEF_FILE ?= data/input/functions_definition.json
IN_FILE ?= data/input/function_calling_tests.json
OUT_FILE ?= data/output/function_calling_results.json

.PHONY: all install run debug lint lint-strict test clean fclean

all: install

install:
	$(CACHE_ENV) $(UV) sync

run:
	$(CACHE_ENV) $(UV) run python -m $(SRC) \
		--functions_definition $(DEF_FILE) \
		--input $(IN_FILE) \
		--output $(OUT_FILE)

debug:
	$(CACHE_ENV) $(UV) run python -m pdb -m $(SRC) \
		--functions_definition $(DEF_FILE) \
		--input $(IN_FILE) \
		--output $(OUT_FILE)

lint:
	$(UV) run flake8 $(SRC)
	$(UV) run mypy $(SRC) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(UV) run flake8 $(SRC)
	$(UV) run mypy $(SRC) --strict

test:
	$(CACHE_ENV) $(UV) run pytest

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache data/output
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

fclean: clean
	rm -rf .venv