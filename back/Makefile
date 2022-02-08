PIPRUN = pipenv run python
DOCKER = docker
DOCKER_COMPOSE = docker-compose


.venv: Pipfile
	PIPENV_VENV_IN_PROJECT=true pipenv install --dev
	touch .venv


.PHONY: deps
deps: .venv


.PHONY: test
test: deps
	${DOCKER_COMPOSE} run --rm --entrypoint="python3 manage.py test" website-migrate

.PHONY: lint
lint: deps
	pipenv run flake8 back/


.PHONY: migrations
migrations: deps
	${PIPRUN} manage.py makemigrations


.PHONY: migrate
migrate:
	${DOCKER_COMPOSE} run website-migrate


.PHONY: fixtures
fixtures:
	${DOCKER_COMPOSE} run --entrypoint="python3 manage.py loaddata --app api user oauth2client" website-migrate


.PHONY: resetdb
resetdb:
	${DOCKER_COMPOSE} run --entrypoint="python3 manage.py reset_db --noinput" website-migrate


.PHONY: resetmigrations
resetmigrations:
	rm -f api/migrations/00*.py
	${MAKE} migrations


.PHONY: shell
shell:
	${DOCKER_COMPOSE} run --entrypoint="python3 manage.py shell" website-migrate
