.PHONY: Makefile
CONTAINER_NAME := mba-scraper

# Docker-related and running stuff inside docker:
dc/% dc_%:  ### Run any action inside docker (replace % with any action from below)
	docker compose run --rm ${CONTAINER_NAME} make $*

# Run all
all: check test ### Run all checks and tests (lints, mypy, tests...)

all_ff: check_ff test ### Run all checks and tests, but fail on first that returns error (lints, mypy, tests...)

# Separate command versions for github actions
ci/test:
	PYTHONPATH=./src pytest tests/ --durations=10 --junit-xml=test-results.xml

ci/check: ci/check/lint/black ci/check/lint/deps ci/check/lint/flake8 ci/check/lint/isort ci/check/mypy

ci/check/lint/black ci/lint/black:
	black src/ --diff --check --quiet

ci/check/lint/deps ci/lint/deps:
	fawltydeps --detailed

ci/check/lint/flake8 ci/lint/flake8:
	flake8 src/

ci/check/lint/isort ci/lint/isort:
	isort src/ --diff --check --quiet

ci/check/mypy ci/lint/mypy:
	PYTHONPATH=./src mypy src/ --show-error-codes --show-traceback --implicit-reexport --junit-xml=mypy-results.xml

check/lint/black lint/black black-check:  ### Run black lint check (code formatting)
	-black src/ --diff --check --color

check_ff/lint/black lint_ff/black:
	black src/ --diff --check --color

check/lint/deps:
	-fawltydeps --detailed

check_ff/lint/deps:
	fawltydeps --detailed

check/lint/flake8 lint/flake8 flake8-check:  ### Run flake8 lint check (pep8 etc.)
	-flake8 src/

check_ff/lint/flake8 lint_ff/flake8:
	flake8 src/

check/lint/isort lint/isort isort-check:  ### Run isort lint check (import sorting)
	-isort src/ --diff --check --color

check_ff/lint/isort lint_ff/isort:
	isort src/ --diff --check --color

check/mypy check_ff/mypy lint/mypy lint_ff/mypy mypy:  ### Run mypy check (type checking)
	PYTHONPATH=./src mypy src/ --show-error-codes --show-traceback --implicit-reexport

check/lint lint: check/lint/black check/lint/deps check/lint/flake8 check/lint/isort  ### Run all lightweight lint checks (no mypy)

check_ff/lint lint_ff: check_ff/lint/black check_ff/lint/deps check_ff/lint/flake8 check_ff/lint/isort  ### Run all lightweight lint checks, but fail on first that returns error

check lint_full full_lint: check/lint check/mypy  ### Run all lint checks and mypy

check_ff lint_full_ff full_lint_ff: check_ff/lint check_ff/mypy  ### Run all lint checks and mypy, but fail on first that returns error

lint_fix lint/fix:  ### Automatically fix lint problems (only reported by black and isort)
	black .
	isort .

test:  ### Run all unittests
	PYTHONPATH=./src pytest tests

bash:  ### Open bash console (useful when prefixed with dc/, as it opens bash inside docker)
	bash

copier_update:  ### Run copier to update project from template
	copier update --answers-file .copier/.copier-answers.copier-python-project.yml --skip-answered

ps:  ### Open python console (useful when prefixed with dc/, as it opens python console inside docker)
	PYTHONPATH=./src PYTHONSTARTUP=ipython_startup.py ipython

generate_requirements:  ### Generate requirements.txt from poetry.lock
	poetry export --without-hashes -f requirements.txt > requirements.txt

install:  ### Install dependencies from requirements.txt
	pip install --target ./package -r requirements.txt

pack:  ### Pack source code into zip package
	cd package && zip -r ../pkg.zip . && cd .. && zip -g pkg.zip src/*

###  Do not run commands below within container (dc_ prefix)
lambda_build_local:  ## Build lambda locally
	# copy to requirements.txt
	make dc_generate_requirements
	sam build --use-container --build-image MBAScraper=public.ecr.aws/sam/build-python3.13 \
		--template template.yaml \
		--debug

lambda_api:  ## Run lambda locally
	sam local start-api -p 3738

lambda_build:  ## Build lambda package
	make generate_requirements
	make install
	make pack

#build package locally which is ready to upload od remote lambda
lambda_build_pack_locally:  ## Build lambda package locally
	make dc_generate_requirements
	make dc_install
	make pack

### Help
help: ## Show this help
	@sed -Ene 's/^([^ 	]+)( [^ 	]+)*:.*##/\1:\t/p' $(MAKEFILE_LIST) | column -t -s $$'\t'
