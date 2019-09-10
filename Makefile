CWD := $(shell pwd)
ARGS := ""

.PHONY: all
all: clean

.PHONY: start
start: env
	@cd examples/javascript && \
		make markdown

.PHONY: install
install: env
	@cd examples/javascript && make install

.PHONY: uninstall
uninstall:
	-@rm -rf env >/dev/null || true
	@cd examples/javascript && make uninstall

.PHONY: reinstall
reinstall: uninstall install
	@cd examples/javascript && make reinstall

.PHONY: format
format:
	@env/bin/yapf -ir -vv \
    $(CWD)/*.py \
    $(CWD)/sphinx_markdown_builder
	@env/bin/unify -ir \
    $(CWD)/*.py \
    $(CWD)/sphinx_markdown_builder

env:
	@virtualenv env
	@env/bin/pip3 install -r ./requirements.txt

.PHONY: build
build: dist

dist: clean install
	@env/bin/python3 setup.py sdist
	@env/bin/python3 setup.py bdist_wheel

.PHONY: publish
publish: dist
	@twine upload dist/*

.PHONY: link
link: install
	@pip3 install -e .

.PHONY: unlink
unlink: install
	-@rm -r $(shell find . -name '*.egg-info') 2>/dev/null | true

.PHONY: clean
clean:
	@git clean -fXd -e \!env -e \!env/**/*

.PHONY: nuke
nuke:
	@git clean -fXd
