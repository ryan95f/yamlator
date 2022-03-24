# Schema components

Below are the various components that can be used to construct a schema in Yamler that can be used to validate a YAML file.

## Rulesets

In Yamler, a ruleset defines the basic validation block that is compared against a YAML file. A ruleset is made up or 1 or more rules.

Below is the basic definition of a user defined ruleset:

```text
ruleset <name> {
    <list of rules>
}
```

## Rules

A rule define the checks that will compared against the Yaml. The name of the rule should match the expect key in the YAML file. For example, if we had the following data:

```yaml
message: hello world
```

The corresponding ruleset and rule would be:

```text
ruleset <ruleset-name> {
    message str
}
```

A ruleset can either be marked as *optional* or *required*. All rules are implicitly required if the option is not specified in the schema file. Below are the different ways a rule can be defined as required or optional:

```text
ruleset <ruleset-name> {
    message <type>                     # Is a required rule
    requiredMessage <type> required    # Is a required rule
    optionalMessage <type> optional    # Is an optional rule
}
```

Required rules validate that the key is present in the YAML data. If the required data is missing then a required violation is raised. If the rule is optional, then a violation is not raised when it is missing from the YAML data.

## Rule Types

### Basic Types

For each rule, the following basic types are supported:

* `int` - Integer type
* `str` - String type
* `list(<type>)` - List type where `<type>` defines the expected type of each item in the list.
* `map(<type>)` - Map Type where `<type>` defines the expected type of the value.

The list and map type support multiple nested structures which allows for complicated structures to be validated. The `<type>` for a map or list can be a ruleset, enum, any or a basic type.

A nested list in a rule can be defined as:

```text
matrix list(list(int))
```

A map of rulesets can be defined as:

```text
employees map((employee))
```

### Any Type

The `any` type allows for a key to be defined that does not require a type check. When the `any` type key is used in a rule all type checks are ignored and any data type may be used. Only the required and optional checks are applied.

An example of it in a ruleset:

```text
ruleset <ruleset-name> {
    message any
    type any optional
}
```

### Ruleset Type

Rulesets can be referenced as a type for a rule to validate complicated YAML structures. For example, the following YAML data existed:

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

Then the ruleset to represent the `project` key data:

```text
ruleset project {
    version str
    id int
    name str
    users list(str) optional
    labels map(str) optional
}
```

Once the `project` ruleset has been defined, it can be used within a another ruleset with:

**Note**: In the ruleset, to reference another ruleset as a type it must be enclosed in brackets.

```text
ruleset <name> {
    project (project)
}
```

### Enum Type

Enums can be used to define string contants in a schema. This can be used to enforce specific string values in the YAML data. An enum must start with a captial level. A enum can be defined with:

```text
enum <enum-name> {
    <key> = <value>
}
```

For example, a enum for log levels could be:

```text
enum LogLevel {
    ERR = error
    INFO = info
    DEBUG = debug
}
```

Like a ruleset, enums can be referanced as a type within a rule. For example:

```text
ruleset <ruleset-name> {
    logLevel LogLevel
}
```
