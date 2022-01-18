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
	${DOCKER_COMPOSE} run --rm --entrypoint="python3 manage.py test" back

.PHONY: lint
lint: deps
	pipenv run flake8 back/


.PHONY: migrations
migrations: deps
	${PIPRUN} manage.py makemigrations


.PHONY: migrate
migrate:
	${DOCKER_COMPOSE} run migrate


.PHONY: resetdb
resetdb:
	${DOCKER_COMPOSE} run --entrypoint="python3 manage.py reset_db --noinput" migrate


.PHONY: shell
shell:
	${DOCKER_COMPOSE} run --entrypoint="python3 manage.py shell" migrate
