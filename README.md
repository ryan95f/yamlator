# Yamler

[![Test](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml/badge.svg)](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml)

Yamler is a cli tool that allows for a schema to be defined as a collection rulesets. When the tool is executed, a YAML file will be compared against the rulesets where a collection of violations will be returned.

## Installing the package

The Yamler package can be installed by PyPi with:

```bash
pip install yamler
```

## Creating a basic schema

## How to run the CLI

Assuming you have a YAML file and a ruleset file, the CLI can be executed with:

```bash
yamler <path-to-yaml-file> -s <path-to-schema>
```

Where `<path-to-yaml-file>` is replaced with the path to your YAML file and `<path-to-schema>` is the path to the schema.

The first argument for the CLI is always the path to the YAML file followed by the followed arguments:

| Flag | Alias | Description | Is Required |
|:-----|:------|:------------|:------------|
| `--schema` | `-s` | The schama that will be used to validate the YAML file | True |
| `--output` | `-o` | Defines the format that will be displayed for the violations. Support values are `table` or `json` | False |

To see the help options for the CLI, run `yamler -h` or `yamler --help`

## Setting up the development environment

For instructions on how to set up the development environment, read the [setting up the environment document](./docs/setting_up_the_environment.md).
