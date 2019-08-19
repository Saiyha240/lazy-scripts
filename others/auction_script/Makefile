.DEFAULT_GOAL := default

build:
	cd test; \
	docker build -t sas .
run:
	cd test; \
	docker run -d -p '8080:80' sas:latest

stop:
	docker stop $(docker ps --filter "ancestor=sas" -q) || true

default: stop build run