# Yamlator

[![Test](https://github.com/ryan95f/yamlator/actions/workflows/test.yaml/badge.svg)](https://github.com/ryan95f/yamlator/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/ryan95f/yamlator/branch/main/graph/badge.svg)](https://codecov.io/gh/ryan95f/yamlator)
[![License](https://img.shields.io/github/license/ryan95f/yamlator)](https://github.com/ryan95f/yamlator/blob/main/LICENSE)
[![PyPi Version](https://img.shields.io/pypi/v/yamlator)](https://pypi.org/project/yamlator/)

Yamlator is a CLI tool that allows a YAML file to be validated using a lightweight schema that defines the expected structure. When executed, the YAML is compared against the rules to validate that the relevant keys and data types are present. Once validated, a list of violations will be displayed to help amend the YAML file.

## Installing the package

The Yamlator package can be installed from PyPi with:

```bash
pip install yamlator
```

## A basic example

Schemas in Yamlator are comprised of rules, rulesets and enums, which are defined in a Yamlator schema file with the `.ys` extension.

In the Yamlator schema file, the entry point is defined in a `schema` block. As a minimum, a schema block must be defined for Yamlator to validate a file. Complex structures can be defined as `rulesets` to validate nested structures. For example, the following schema can be defined to manage a list of employees:

```text
ruleset Employee {
    firstName str
    lastName str
    roles list(str) optional
}

schema {
    employees list(Employee)
}
```

This schema can then be used to validate the following YAML data:

```yaml
employees:
    - firstName: employee
      lastName: one
      roles:
        - manager
    - firstName: employee
      lastName: two
      roles:
        - engineer
        - manager
    - firstName: employee
      lastName: three
```

More information on the different components that can be used in a schema can be found in the [schema components documentation](./docs/schema_components.md).

Additional examples of Yamlator schemas can be found in the [examples directory](./example/)

## How to run the CLI

Assuming you have a YAML and Yamlator schema file, the CLI can be executed with:

```bash
yamlator <path-to-yaml-file> -s <path-to-yamlator-schema>
```

Where `<path-to-yaml-file>` is replaced with the path to your YAML file and `<path-to-yamlator-schema>` is the path to the schema file which must have the `.ys` extension.

The first argument for the CLI is always the path to the YAML file.

| Flag | Alias | Description | Is Required |
|:-----|:------|:------------|:------------|
| `--schema` | `-s` | The schema that will be used to validate the YAML file | True |
| `--output` | `-o` | Defines the violations format that will be displayed. Supported values are `table`, `yaml` or `json`. Defaults to `table` if not specified. | False |

To see the help options for the CLI, run `yamlator -h` or `yamlator --help`

## Setting up the development environment

For instructions on how to set up the development environment, read the [setting up the environment documentation](./docs/setting_up_the_environment.md).
