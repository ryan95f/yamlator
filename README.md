# Yamler

[![Test](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml/badge.svg)](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml)

A parser built using Lark to validate that a `.yaml` / `.yml` file contains a set of required fields.

## Requirements

The project requires the following:

* Python 3.7 or above

## Setting up the environment

To set up the environment, ensure the virtualenv package has been installed. This can be added to your Python instance with:

```bash
pip install virtualenv
```

Once `virtualenv` has been installed. A new virtual environment can be created with:

```bash
python -m venv env
```

Then activate the virtual environment witb:

```bash
# For Windows
./env/Scripts/activate

# For Linux / MacOS
source env/bin/activate
```

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running Yamler

To run the yamler demo:

```bash
python main.py
```

## Running the Tests

This project uses `unittest` and `coverage`. The tests must be executed first before the coverage report can be shown.

To run the tests:

```bash
coverage run -m unittest
```

The coverage report can then be shown with:

```bash
coverage report -m
```

## Coding Standards

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding standard. To validate the code run with `pycodestyle` linter with:

```bash
pycodestyle .
```

## Running the example

To run the example:

```bash
python -m yamler example/hello.yaml -s example/hello.yamler
```
