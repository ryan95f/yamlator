# Schema components

Below are the various components that can be used to construct a schema with Yamlator. These constructs must be placed into a `.ys` file.

## Schema

A schema block defines the entry point that will be used during the validation process. Within the block a list of rules can be defined to indicate the root keys of a YAML file. For example, given the following YAML data:

```yaml
message: Hello World
number: 42
```

The following schema block can be defined:

```text
schema {
    message str
    number int optional
}
```

Rules in the schema block following the exact same pattern that can be used in `rulesets`. See [rules](#rules) for more information.

## Rulesets

A ruleset allows for complex YAML structures to be defined. A ruleset is made up or 1 or more [rules](#rules) and the name of the ruleset must begin with a capital letter.

Below is the basic definition of a user defined ruleset:

```text
ruleset <ruleset-name> {
    <list of rules>
}
```

An example of a ruleset:

```text
ruleset Project {
    version str
    id int
    name str
    users list(str) optional
    labels map(str) optional
}
```

## Rules

A rule defines the basic checks that will compared against the YAML file. The name of the rule should match the expected key in the YAML file. For example, if we had the following data:

```yaml
message: hello world  # This is a required field
```

The corresponding rule in a ruleset would be:

```text
ruleset <ruleset-name> {
    message str
}
```

A rule can either be marked as *optional* or *required*. All rules are implicitly required unless specified. Below are the different ways a rule can be defined as required or optional:

```text
ruleset <ruleset-name> {
    message <type>                     # Is a required rule
    requiredMessage <type> required    # Is a required rule
    optionalMessage <type> optional    # Is an optional rule
}
```

Required rules validate that the key is present in the YAML data. If the required data is missing then a required violation is raised. If the rule is optional, then a violation is not raised when it is missing from the YAML data.

## Rule Types

For each rule, a type can be specified to ensure that data meet the expect type.

### Basic Types

For each rule, the following basic types are supported:

* `int` - Integer type
* `float` - Float type
* `str` - String type
* `list(<type>)` - List type where `<type>` defines the expected type of each item in the list.
* `map(<type>)` - Map Type where `<type>` defines the expected type of the value.

The list and map types support multiple nested structures which allows for complicated structures to be validated. The `<type>` for a map or list can be a ruleset, enum, any or a basic type.

A nested list in a rule can be defined as:

```text
matrix list(list(int))
```

A map of rulesets can be defined as:

```text
employees map(Employee)
```

### Any Type

The `any` type allows for a key to be defined that does not require a type check. When the `any` type key is defind, all type checks are ignored and any data type may be used. When used only the required and optional checks are applied.

An example of it in a ruleset:

```text
ruleset <ruleset-name> {
    message any         # Required any value
    type any optional   # Optional any value
}
```

### Regex Type

The `regex` type allows for a string value to be compared against a regular expression. For example, given the following string in YAML:

```yaml
name: Person1
```

The following regex rule can be defined in a schema block:

```text
schema {
    name regex("^Person")
}
```

Or using a ruleset with:

```text
ruleset <ruleset-name> {
    name regex("^Person")
}
```

The regex type can also be nested in the `map` or `list` types. For example, when applied to a list, it allows for a collection of strings to be validated:

```yaml
roles:
    - role/user
    - role/admin
    - role/editor
```

Then the following rule within a schema block can be used to validate this list:

```text
schema {
    roles list(regex("^role/[a-z]+"))
}
```

### Ruleset Type

Rulesets can be referenced as a type to validate complex YAML structures. For example, if the following YAML data existed:

```yaml
project:
    version: v1
    id: 100
    name: my-awesome-project
    users:
        - user1
        - user2
        - user3
    labels:
        label1: value1
        label2: value2
```

Then the ruleset to represent the `project` key data would be:

```text
ruleset Project {
    version str
    id int
    name str
    users list(str) optional
    labels map(str) optional
}
```

Once the `Project` ruleset has been defined, it can be used within a ruleset with:

```text
ruleset <name> {
    project Project
}
```

Or within a schema block:

```text
schema {
    project Project
}
```

### Enum Type

Enums can be used to define a collection of string, integer and float constants. An enum name must start with a capital letter. A enum can be defined with:

```text
enum <enum-name> {
    <key> = <value>
}
```

For example, a enum of string constants for log levels:

```text
enum LogLevel {
    ERR = "error"
    INFO = "info"
    DEBUG = "debug"
}
```

An example of an enum with integers and floats:

```text
enum Numbers {
    LIFE = 42
    PI = 3.142
}
```

Like a ruleset, enums can be referenced as a type within a rule. For example in a ruleset:

```text
ruleset <ruleset-name> {
    logLevel LogLevel
}
```

Or in a schema block:

```text
Schema {
    logLevel LogLevel
}
```
