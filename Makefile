install-dev-deps: dev-deps
	pip-sync requirements.txt dev-requirements.txt

install-deps: deps
	pip-sync requirements.txt

deps:
	pip-compile --resolver=backtracking --output-file=requirements.txt pyproject.toml

dev-deps: deps
	pip-compile --resolver=backtracking --extra=dev --output-file=dev-requirements.txt pyproject.toml

lint:
	flake8 *.py
	mypy

fmt:
	isort .

test:
	pytest --dead-fixtures
	pytest -x

dev:
	watchmedo auto-restart --patterns '*.py' python bot.py

