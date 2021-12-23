DOCKER_COMPOSE=docker-compose


.PHONY: build
build:
	${DOCKER_COMPOSE} build


.PHONY: run
run:
	${DOCKER_COMPOSE} up
