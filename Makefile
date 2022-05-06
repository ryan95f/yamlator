all: test build
	
build:
	python setup.py sdist bdist_wheel

test:
	coverage run -m unittest
	coverage report -m

clean:
	rm -rf build/ yamlator.egg-info/ dist/ .coverage