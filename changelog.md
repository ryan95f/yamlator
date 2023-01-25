# Changelog

## v0.0.1 (6th April 2022)

* Initial release of the Yamlator package

## v0.1.0 (15th May 2022)

* Added a `Regex` type to the schema to support regex validation
* Added support for `integers` and `floats` in the `Enum` construct
* Fixed bug with the the `Enum` and `Ruleset` construct names that prevented camel case from working
* Updated the source code package from `src` to `yamlator`
* General improvements to existing documentation

## v0.1.1 (26th May 2022)

* Updated urls in the `README.md` and `setup.py` to reflect the username change

## v0.1.2 (25th September 2022)

* Added `Pylint` to the `test` workflow pipeline
* Added a new `CodeQL` workflow pipeline
* Added `YAML` as a display option using the CLI
* Updated docstrings in the `validators` package
* Updated `cmd.py` to be a sub package in `yamlator` to improve code readability

## v0.2.0 (8th January 2023)

* Added `strict` keyword to rulesets to enable strict mode, which will raise a strict violation for every field not defined in the ruleset
* Added `strict` keyword to schema to enable strict mode, which will raise a strict violation for every field not defined in the schema block
* Added new example [strict_mode](./example/strict_mode/) to the `example` directory
* Updated GitHub workloads to use the latest actions
* Fixed bug with rule definitions where field names with similar character patterns to types would create two separate rules

## v0.2.1 (15th January 2023)

* Improved the Yamlator grammar to allow rule names to accept options including symbols, unicode, spaces and dashes. Any YAML key that contains spaces, must be enclosed in double quotes
* Upgraded the Ubuntu version on the publish workflow

## v0.2.2 (18th January 2023)

* Added support for Python 3.6+ by removing the `__future__` and `dataclass` imports from the codebase
* Downgraded pylint in the developer dependencies to allow for Python 3.6 to run locally

## v0.3.0 (TBC)

* Added the `union` data type tp the schema to allow a field to allow a key to have more than one specific type
* Reduced the constraints on the `install_requirements`
* Minor fixes and improvements to the overall codebase
