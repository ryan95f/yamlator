# Schema Types

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
* `list(<type>)` - List type
* `map(<type>)` - Map Type

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

### Enum Type
