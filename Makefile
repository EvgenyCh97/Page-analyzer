install:
	poetry install

package-install:
	python3 -m pip install --user dist/*.whl

selfcheck:
	poetry check

test:
	poetry run pytest

lint:
	poetry run flake8 page_analyzer tests

check: selfcheck test lint

build_package: check
	poetry build

reinstall: build_package package-install
	pip install --user dist/*.whl --force-reinstall

full-reinstall: build_package package-install reinstall

test-coverage:
	poetry run pytest --cov=page_analyzer tests/ --cov-report xml tests

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8001
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

make db_conenct:
	PGPASSWORD=In3nqr68N1Mit7NYy9gWpDJcV4Ewxvrt psql -h dpg-ckj9s18lk5ic73di4amg-a.oregon-postgres.render.com -U page_analyzer_hfq0_user page_analyzer_hfq0

.PHONY: install test lint selfcheck check build
