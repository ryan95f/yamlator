# Rulesets

In Yamler, a ruleset defines the basic validation block that is compared against a YAML file. A ruleset is made up or 1 or more rules.

Below is the basic definition of a user defined ruleset:

```text
ruleset <name> {
    ...
}
```

In order for a ruleset to be executed by Yamler, it needs to be attached to the *main ruleset*. This acts as an entry point for Yamler to start the validation process. The definition of a main ruleset:

```text
ruleset main {
    ...
}
```

## Rules

Each roleset has one or more rules. These define the checks that will compared against the Yaml. A rule can be defined as either **optional** or **required**. Each rule starts with the name of the key to look for in the Yaml file, followed by a type and if required / not.

To define a key with a required string:

```text
hello str required
```

Other rulesets can be linked up to a ruleset. A special syntax `(<ruleset_name>)` around the type to indicates it is a ruleset. For example:

```text
ruleset person {
    name str required
}

ruleset details {
    person (person) required
}
```
