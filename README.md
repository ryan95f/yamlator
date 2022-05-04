# Yamlator

[![Test](https://github.com/Ryan95Z/yamlator/actions/workflows/test.yaml/badge.svg)](https://github.com/Ryan95Z/yamlator/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/Ryan95Z/yamlator/branch/main/graph/badge.svg)](https://codecov.io/gh/Ryan95Z/yamlator)
[![License](https://img.shields.io/github/license/Ryan95Z/yamlator)](https://github.com/Ryan95Z/yamlator/blob/main/LICENSE)
[![PyPi Version](https://img.shields.io/pypi/v/yamlator)](https://pypi.org/project/yamlator/)

Yamlator is a CLI tool that allows a YAML file to be validated against a lightweight schema that defines the expected structure for the YAML file. When executed, the YAML data is compared against the rules to validate that the relevant keys and data types are present. Once validated, a list of violations will be displayed to help amend the YAML data.

## Installing the package

The Yamlator package can be installed from PyPi with:

```bash
pip install yamlator
```

## Creating a basic schema

Schemas in Yamlator are comprised of rules, rulesets and enums, which are defined in a Yamlator schema (with a `.ys` extension) file.

In the Yamlator schema, the entry point is defined in a `schema` block. As a minimum, a schema block must be defined for Yamlator to validate a file. For example:

```text
schema {
    name str
    age int
}
```

This can be used to validate the following YAML file:

```yaml
name: Name
age: 100
```

With Yamlator, more complex structures can be defined as `rulesets` to validate nested structures. For example:

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

This can then be used to validate the following YAML data:

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

More information on the different components that make up a schema can be found in the [schema components document](./docs/schema_components.md).

Some examples of a schema file with a YAML file can be found in the [examples directory](./example/)

## How to run the CLI

Assuming you have the YAML and Yamlator files, the CLI can be executed with:

```bash
yamlator <path-to-yaml-file> -s <path-to-yamlator-schema>
```

Where `<path-to-yaml-file>` is replaced with the path to your YAML file and `<path-to-yamlator-schema>` is the path to the schema, which has the extension `.ys`.

The first argument for the CLI is always the path to the YAML file.

| Flag | Alias | Description | Is Required |
|:-----|:------|:------------|:------------|
| `--schema` | `-s` | The schema that will be used to validate the YAML file | True |
| `--output` | `-o` | Defines the format that will be displayed for the violations. Supported values are `table` or `json`. Defaults to `table` if not specified. | False |

To see the help options for the CLI, run `yamlator -h` or `yamlator --help`

## Setting up the development environment

For instructions on how to set up the development environment, read the [setting up the environment document](./docs/setting_up_the_environment.md).
