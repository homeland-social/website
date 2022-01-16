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


.PHONY: rebuild
rebuild:
	${DOCKER_COMPOSE} stop ${SERVICE}
	${DOCKER_COMPOSE} rm -f ${SERVICE}
	${DOCKER_COMPOSE} build ${SERVICE}
	${DOCKER_COMPOSE} create ${SERVICE}
	${DOCKER_COMPOSE} start ${SERVICE}


.PHONY: ci
ci: test lint