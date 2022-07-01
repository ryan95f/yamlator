# Setting up the development environment

## Requirements

The project requires the following:

* Python 3.7 or above

## Creating the virtual environment

Before creating a virtual environment, ensure that the `virtualenv` package has been installed. This can be installed with:

```bash
pip install virtualenv
```

Once `virtualenv` has been installed. A new virtual environment can be created with:

```bash
python3 -m venv env
```

Then activate the virtual environment with:

```bash
# For Windows
./env/Scripts/activate

# For Linux / MacOS
source env/bin/activate
```

Once the virtual environment has been activated, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Unit Tests

This project uses `unittest` and `coverage`. To run the tests with coverage, use:

```bash
coverage run -m unittest
```

The coverage report can then be shown with:

```bash
coverage report -m
```

## Coding Standards

This project uses the [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding standard. To run the `pycodestyle` linter, use:

```bash
pycodestyle .
```

This project also uses `pylint` to run static code analysis checks using the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) configuration.

To run the check over the Yamlator source code:

```bash
pylint yamlator/
```

Then to apply this check to the test cases:

```bash
pylint tests/
```
