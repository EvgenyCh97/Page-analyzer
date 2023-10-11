install:
	poetry install

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 gendiff tests

build_package: check
	poetry build

reinstall: build_package package-install
	pip install --user dist/*.whl --force-reinstall

full-reinstall: build_package package-install reinstall

test-coverage:
	poetry run pytest --cov=gendiff tests/ --cov-report xml tests

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

.PHONY: install test lint selfcheck check build
