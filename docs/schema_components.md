# Schema components

Below are the various components that can be used to construct a schema with Yamlator. These constructs must be placed into a schema file which ends with `.ys` extension.

* [Schema](#schema)
* [Rulesets](#rulesets)
* [Strict Mode](#strict-mode)
  * [Schema](#schema---strict-mode)
  * [Ruleset](#ruleset---strict-mode)
* [Rules](#rules)
  * [Top Level Validation without a key](#top-level-validation-without-a-key)
* [Enums](#enums)
* [RuleTypes](#rule-types)
  * [Basic Types](#basic-types)
  * [Any Type](#any-type)
  * [Regex Type](#regex-type)
  * [Ruleset Type](#ruleset-type)
  * [Enum Type](#enum-type)
  * [Union Type](#union-type)
* [Importing schemas](#importing-schemas)
  * [Schema import paths](#schema-import-paths)
* [Ruleset Inheritance](#ruleset-inheritance)
  * [Strict ruleset inheritance](#strict-ruleset-inheritance)
  * [Inheritance from imported schemas](#inheritance-from-imported-schemas)

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

Rules in the schema block follow the exact same pattern that can be used in `rulesets`. See [rules](#rules) for more information.

## Rulesets

A ruleset allows for complex YAML structures to be defined. A ruleset is made up of 1 or more [rules](#rules). The name of the ruleset must begin with a capital letter followed by lowercase letters, uppercase letters or underscores.

The following are valid ruleset names:

* `Employee`
* `EmployeeDetails`
* `Employee_Details`
* `Employeedetails`
* `Employee_details`

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

## Strict Mode

A schema and ruleset block can be set into strict mode to raise violation errors when fields in the YAML file are not defined in the schema/ruleset block. For every field that is not expected in the block a strict violation is raised.

To use strict mode, the ruleset or schema block should be prefixed with the `strict` keyword.

__NOTE__: Strict mode does not cascade down to other rulesets when defined against a schema or ruleset. Strict mode must be defined on each block that requires it.

### Schema - Strict Mode

For example, given the following schema block:

```text
strict schema {
    message str
    number int optional
}
```

Then given the following YAML data:

```yaml
message: Hello World
number: 42
firstName: foo
lastName: bar
```

The fields `firstName` and `lastName` will have strict mode violations raised since it does not match the schema block.

### Ruleset - Strict Mode

For example, given the following ruleset:

```text
strict ruleset Person {
    firstName str
    lastName str
}
```

Then the following YAML data:

```yaml
firstName: Foo
lastName: Bar
fullName: Foo Bar
age: 42
```

The fields `fullName` and `age` will have strict mode violations raised since it does not match the fields specified in the ruleset block.

## Enums

Enums can be used to define a collection of string, integer and float constants. An enum name must start with a capital letter followed by lowercase letters, uppercase letters or underscores.

The following are valid enum names:

* `Status`
* `EmployeeStatus`
* `Employee_Status`
* `Employeestatus`
* `Employee_status`

A enum can be defined with:

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

Rule names support dashes, underscores and all unicode characters. If the field name in YAML contains spaces, e.g `my awesome field`, then the rule name will need to be enclosed in double quotes. For example, given the following YAML data:

```yaml
my awesome field: 42
```

The corresponding rule name in a ruleset:

```text
ruleset <ruleset-name> {
    "my awesome field" int
}
```

### Top level validation without a key

Not all YAML files use objects or maps at the top of the data structure. Lists or other data types might be used at the very top level.

In order for Yamlator to validate data structures like this, a reserved rule name called `!!yamlator` can be used to perform this sort of validation. For example, given the following YAML data:

```yaml
- 1
- 2
- 3
```

The following YAML schema can be defined to validate the list of integers:

```text
schema {
    !!yamlator list(int)
}
```

All supported types can be used to perform top level validation including maps, lists, unions, regex, integers, strings and rulesets.

__NOTE__: The schema block when performing top level validation will expect exactly __one rule__. If additional rules are added then Yamlator will assume there is an object with multiple keys to validate and will expect a key called `!!yamlator` in the data structure.

## Rule Types

For each rule, a type can be specified to validate the expected data type is present.

### Basic Types

For each rule, the following basic types are supported:

* `int` - Integer type
* `float` - Float type
* `str` - String type
* `bool` - Boolean type
* `list(<type>)` - List type where `<type>` defines the expected type of each item in the list.
* `map(<type>)` - Map type where `<type>` defines the expected type of the value.

The list and map types support multiple nested structures which allows for complicated structures to be validated. The `<type>` for a map or list can be a ruleset, enum, list, map, any, regex or a basic type.

A nested list in a rule can be defined as:

```text
matrix list(list(int))
```

A map of rulesets can be defined as:

```text
employees map(Employee)
```

### Any Type

The `any` type allows for a key to be defined that does not require a type check. When the `any` type key is used, all type checks are ignored and any data type may be used in the YAML data. When used only the required and optional checks are applied.

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

Once the `Project` ruleset has been defined, it can be used as a rule type within a ruleset:

```text
ruleset <ruleset-name> {
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

Enums can be referenced as a type within a rule to validate that a key matches the constant value. For example, given the following YAML data:

```yaml
logMessage:
    logLevel: error
    message: An issue has occurred
```

Then a enum could represent the log levels with:

```text
enum LogLevel {
    ERR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
}
```

Once we have the Enum, it can be used as a rule type for a ruleset with:

```text
ruleset <ruleset-name> {
    logLevel LogLevel
}
```

Or in a schema block:

```text
schema {
    logLevel LogLevel
}
```

### Union Type

The `union` type can be used when a key could be one or more types. For example, a key could be either an `int` or a `float`. The union type supports all available types including lists, rulesets, regex, enums, maps and all the other basic types. When defining a `union`, 2 or more types must be defined for it to be valid.

Nested `unions` are *NOT* supported and will raise a parsing error. Unions can be nested in other data types such as a list, rulesets and maps which can then used within a `union`. However direct nesting of unions is not supported.

__Note__: The union will always return a single violation if one or more data types are not met. It currently does not display the individual violations against each type.

An example of a `union` type:

```yaml
items:
    - name: item1
      price: 10
    - name: item2
      price: 15.2
```

Then the following schema can be defined:

```text
ruleset Item {
    name str
    price union(int, float)
}

schema {
    items list(Item)
}
```

## Importing Schemas

As of version `0.4.0`, Yamlator now supports importing rulesets and enums from other schema files. A single import statement can import one or more resources. Imports can also be given an optional namespace to support importing multiple resources with the same name from different schemas. For example, below is an import statement structure without a namespace:

```text
import <COMMA SEPARATED LIST OF RESOURCES> from <RESOURCE PATH>
```

Or an import statement with a namespace:

```text
import <COMMA SEPARATED LIST OF RESOURCES> from <RESOURCE PATH> as <NAMESPACE>
```

For example, given the schema called `main.ys`, which is importing resources from two different schemas:

```text
import Api from "../web/apis.ys"
import Status, ProjectDetails from "common.ys" as core

schema {
    project Project
}

strict ruleset Project {
    status core.Status
    apis list(Api)
    details core.ProjectDetails
}
```

Any imported resources that use a namespace must have the namespace and the resource type specified in the rule type. For example, in the case of importing `ProjectDetails`, which is coming from the `core` namespace, you can see that the rule type is `core.ProjectDetails`. If the namespace is omitted for an imported resource that uses a namespace, a unknown type error will be shown and Yamlator will exit with a non-zero status code.

__NOTE__: Importing schema blocks and using wildcards (typically seen as `*`) to import every resource are not supported in Yamlator.

### Schema import paths

When importing a schema, the path is the location of the schema relative to schema that is using its resources. For example, given the schema above, it would exist in the following file structure:

```text
web/
    apis.ys
main/
    common.ys
    main.ys
```

The `apis` will be fetched from the `web` directory and `common.ys` is located in the same directory location as the `main.ys` file. An full example of importing schemas can be found in [example folder](../example/imports/).

__NOTE__: If an import cycle is detected, Yamlator will exit with a non-zero status code.

## Ruleset Inheritance

In Yamlator version `0.4.1`, rulesets can now inherit other rulesets to reduce duplicating rules. A Ruleset can inherited other rulesets from the current schema or from schemas that has been imported.

__NOTE__: A ruleset can only inherit a single ruleset. Multi-inheritance is currently __NOT__ supported.

An example of ruleset inheritance where the `Employee` ruleset will inherit the rules from the `Person` ruleset:

```text
ruleset Person {
    first_name str
    surname str
}

ruleset Employee(Person) {
    employee_id str
}
```

The `Employee` ruleset will now contain a total of 3 rules, 2 from the `Person` ruleset and 1 rule from its own block.

If a child ruleset has a rule with the same name as the inherited ruleset, then the child rule will override the parent. For example, given the following example:

```text
ruleset Versions {
    version str
    kind str
}

ruleset Foo(Versions) {
    version int
}
```

In this case, the `Foo` ruleset will only have 2 rules. The `kind` rule will be inherited but the `version` rule in `Foo` will override the exiting rule in `Versions`.

### Strict Ruleset Inheritance

If the parent ruleset is a strict ruleset, strict mode will __NOT__ be inherited by the child ruleset. In order for the child ruleset to use strict mode, it must specify it is a strict ruleset in its definition. For example:

```text
strict ruleset Foo {
    bar str
    baz int
}

ruleset Request1(Foo) {
    id str
}

strict ruleset Request2(Foo) {
    id str
}
```

In the above case, the ruleset `Request1` will not enforce strict mode. However `Request2` will enforce strict mode since it has been defined as a strict ruleset.

### Inheritance from imported schemas

Rulesets can be inherited by rulesets from other files that have been imported with/without a namespace. For example:

Given the below ruleset is located in a file called `common.ys`

```text
ruleset Project {
    id str
    version str
    kind str
}
```

This ruleset can then imported with or without a namespace and be inherited:

```text
import Project from "common.ys" as common
import Project from "common.ys"

ruleset AwesomeProject1(common.Project) {
    ...
}

ruleset AwesomeProject2(Project) {
    ...
}
```

__NOTE__: If a inheritance cycle is detected, Yamlator will exit with a non-zero status code.
