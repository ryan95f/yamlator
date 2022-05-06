all: lint test build
	
build:
	python setup.py sdist bdist_wheel

lint:
	pycodestyle .

test:
	coverage run -m unittest
	coverage report -m

clean:
	rm -rf build/ yamlator.egg-info/ dist/ .coverage