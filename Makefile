CWD := $(shell pwd)
ARGS := ""

.PHONY: all
all: clean

.PHONY: start
start: env
	@env/bin/python3 anydb $(ARGS)

.PHONY: install
install: env

.PHONY: uninstall
uninstall:
	-@rm -rf env >/dev/null || true

.PHONY: reinstall
reinstall: uninstall install

env:
	@virtualenv env
	@env/bin/pip3 install -r ./requirements.txt
	@echo ::: ENV :::

.PHONY: freeze
freeze:
	@env/bin/pip3 freeze > ./requirements.txt
	@echo ::: FREEZE :::

.PHONY: build
build: dist

dist: clean install
	@env/bin/python3 setup.py sdist
	@env/bin/python3 setup.py bdist_wheel
	@echo ran dist

.PHONY: publish
publish: dist
	@twine upload dist/*
	@echo published

.PHONY: link
link: install
	@pip3 install -e .

.PHONY: unlink
unlink: install
	@rm -r $(shell find . -name '*.egg-info')

.PHONY: clean
clean:
	-@rm -rf */__pycache__ */*/__pycache__ README.rst dist build \
		example/.tmp *.egg-info >/dev/null || true
	@echo ::: CLEAN :::
