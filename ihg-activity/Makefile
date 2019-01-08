# IHG Activity Scraper

SHELL = /bin/bash
PYTHON_EXE = python3
TOPDIR = $(shell git rev-parse --show-toplevel)

help: # Display help
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {\
			printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
		}' $(MAKEFILE_LIST)

venv: venv/bin/activate ## Build virtual environment

venv/bin/activate: requirements.txt requirements-dev.txt
	if [ ! -d venv ]; then \
		virtualenv -p $(PYTHON_EXE) venv; \
		. venv/bin/activate; \
			pip install -U pip; \
			pip install -r requirements.txt; \
			pip install -r requirements-dev.txt; \
	fi
	. venv/bin/activate

clean: ## Delete all generated artifacts
	$(RM) -rf venv dist __pycache__ *.egg-info .coverage nohup.out
	find . -name "*.pyc" -delete

docker-build: ## Build a docker image
	docker build -t ihg-activity-scraper .

docker-run: ## Run docker image
	docker run ihg-activity-scraper
