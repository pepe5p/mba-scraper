set dotenv-load

PATHS_TO_LINT := "mba_scraper tests"
TEST_PATH := "tests"
ANSWERS_FILE := ".copier/.copier-answers.copier-python-project.yml"
BUILD_DIR := "build"
CURRENT_DATETIME := `date +'%Y%m%d_%H%M%S'`
PYTHON_VERSION := "3.13"

[doc("Command run when 'just' is called without any arguments")]
default: help

[doc("Show this help message")]
@help:
	just --list

[group("development")]
[doc("Run all checks and tests (lints, mypy, tests...)")]
all: lint_full test

[group("development")]
[doc("Run all checks and tests, but fail on first that returns error (lints, mypy, tests...)")]
all_ff: lint_full_ff test

[group("lint")]
[doc("Run ruff lint check (code formatting)")]
ruff:
	uv run ruff check {{PATHS_TO_LINT}}
	uv run ruff format {{PATHS_TO_LINT}} --check

[group("copier")]
[doc("Update project using copier")]
copier_update answers=ANSWERS_FILE skip-answered="true":
	uv run copier update --answers-file {{answers}} \
	{{ if skip-answered == "true" { "--skip-answered" } else { "" } }}

[group("lint")]
[doc("Run fawltydeps lint check (deopendency issues)")]
deps:
	uv run fawltydeps

[group("lint")]
[doc("Run all lightweight lint checks (no mypy)")]
@lint:
	-just deps
	-just ruff

[group("lint")]
[doc("Run all lightweight lint checks, but fail on first that returns error")]
lint_ff: deps ruff

[group("lint")]
[doc("Automatically fix lint problems (only reported by ruff)")]
lint_fix:
	uv run ruff check {{PATHS_TO_LINT}} --fix
	uv run ruff format {{PATHS_TO_LINT}}

[group("lint")]
[doc("Run all lint checks and mypy")]
lint_full: lint mypy
alias full_lint := lint_full

[group("lint")]
[doc("Run all lint checks and mypy, but fail on first that returns error")]
lint_full_ff: lint_ff mypy
alias full_lint_ff := lint_full_ff

[group("lint")]
[doc("Run mypy check (type checking)")]
mypy:
	uv run mypy {{PATHS_TO_LINT}} --show-error-codes --show-traceback --implicit-reexport

[group("development")]
[doc("Run IPython with custom startup script")]
ps startup_script="ipython_startup.py":
	PYTHONSTARTUP={{ startup_script }} uv run ipython
alias ipython := ps

[group("development")]
[doc("Run non-integration tests (optionally specify file=path/to/test_file.py)")]
test file=TEST_PATH:
	uv run pytest {{file}} --durations=10

[group("lambda_build")]
build: build_create_env
	cd {{ BUILD_DIR }}/pkg && \
	zip -r ../mba_scraper_{{ CURRENT_DATETIME }}.zip .

[group("lambda_build")]
build_create_env: clear_build_dir build_generate_requirements build_install copy_shim

[group("lambda_build")]
clear_build_dir:
	rm -rf {{ BUILD_DIR }}/pkg

[group("lambda_build")]
build_generate_requirements:
	uv export --frozen --no-dev --no-editable -o {{ BUILD_DIR }}/requirements.txt

[group("lambda_build")]
build_install:
	uv pip install \
	--no-installer-metadata \
	--no-compile-bytecode \
	--python-platform x86_64-manylinux2014 \
	--python {{ PYTHON_VERSION }} \
	--target {{ BUILD_DIR }}/pkg \
	-r {{ BUILD_DIR }}/requirements.txt

[group("lambda_build")]
copy_shim:
    cp lambda_function.py {{ BUILD_DIR }}/pkg/ || true
