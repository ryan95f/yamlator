# Yamler

[![Test](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml/badge.svg)](https://github.com/Ryan95Z/yamler/actions/workflows/test.yaml)

Yamler is a CLI tool that allows a YAML file to be validated against a schema. When executed, the YAML data structure is compared against the rules to validate that the required keys are present and the data type is correct. Once the YAML file has been validated, a list of violations will be returned that can be used to amend the file.

## Installing the package

The Yamler package can be installed by PyPi with:

```bash
pip install yamler
```

## Creating a basic schema

Schemas in Yamler are comprised of a set of rulesets and enums. As a minimum, a ruleset named `main` must be provided. For example:

```text
ruleset main {
    name str
    age int
}
```

The ruleset must be saved as a `.yamler` file, which can be used to validate the following YAML file:

```yaml
name: Name
age: 100
```

With Yamler, more complex structures can be defined to validate nested structures. For example:

```text
ruleset employee {
    firstName str
    lastName str
    roles list(str) optional
}

ruleset main {
    employees list((employee))
}
```

This can then be used to validate the following YAML data:

```yaml
employees:
    - firstName: employee
      lastName: one
      departments:
        - manager
    - firstName: employee
      lastName: two
      departments:
        - engineer
        - manager
    - firstName: employee
      lastName: three
```

More information on the different components that make up a schema, read the [schema components document](./docs/schema_components.md).

## How to run the CLI

Assuming you have a YAML file and a ruleset file, the CLI can be executed with:

```bash
yamler <path-to-yaml-file> -s <path-to-schema>
```

Where `<path-to-yaml-file>` is replaced with the path to your YAML file and `<path-to-schema>` is the path to the schema.

The first argument for the CLI is always the path to the YAML file.

| Flag | Alias | Description | Is Required |
|:-----|:------|:------------|:------------|
| `--schema` | `-s` | The schema that will be used to validate the YAML file | True |
| `--output` | `-o` | Defines the format that will be displayed for the violations. Support values are `table` or `json`. Defaults to `table` if not specified. | False |

To see the help options for the CLI, run `yamler -h` or `yamler --help`

## Setting up the development environment

For instructions on how to set up the development environment, read the [setting up the environment document](./docs/setting_up_the_environment.md).
