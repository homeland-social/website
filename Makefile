DOCKER_COMPOSE=docker-compose


.PHONY: build
build:
	${DOCKER_COMPOSE} build


.PHONY: run
run:
	${DOCKER_COMPOSE} up


.PHONY: test
test:
	${MAKE} -C front test
	${MAKE} -C back test


.PHONY: lint
lint:
	${MAKE} -C front lint
	${MAKE} -C back lint


.PHONY: ci
ci: test lint