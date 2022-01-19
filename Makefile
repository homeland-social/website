DOCKER = docker
DOCKER_COMPOSE = docker-compose -p website


.PHONY: shared
shared:
	-${DOCKER} network create --subnet=192.168.100.0/24 --ip-range=192.168.100.0/25 --gateway=192.168.100.254 shared


.PHONY: build
build:
	${DOCKER_COMPOSE} build


.PHONY: run
run: shared
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
ifdef SERVICE
	${DOCKER_COMPOSE} stop ${SERVICE}
	${DOCKER_COMPOSE} rm -f ${SERVICE}
	${DOCKER_COMPOSE} build ${SERVICE}
	${DOCKER_COMPOSE} create ${SERVICE}
	${DOCKER_COMPOSE} start ${SERVICE}
else
	@echo "Please define SERVICE variable, ex:"
	@echo "make rebuild SERVICE=foo"
endif


.PHONY: clean
clean:
	${DOCKER_COMPOSE} rm


.PHONY: resetdb
resetdb:
	$(MAKE) -C back resetdb


.PHONY: resetmigrations
resetmigrations:
	$(MAKE) -C back resetmigrations


.PHONY: ci
ci: test lint
