"""Provides the core functions and entry point to the
validator handler chian.
"""

from collections import deque
from yamlator.types import YamlatorRuleset

from yamlator.validators import AnyTypeValidator
from yamlator.validators import BuiltInTypeValidator
from yamlator.validators import EnumTypeValidator
from yamlator.validators import ListValidator
from yamlator.validators import MapValidator
from yamlator.validators import OptionalValidator
from yamlator.validators import RegexValidator
from yamlator.validators import RequiredValidator
from yamlator.validators import RulesetValidator
from yamlator.validators import EntryPointValidator
from yamlator.validators import UnionValidator
from yamlator.validators.base_validator import Validator


def validate_yaml(yaml_data: dict, instructions: dict) -> deque:
    """Validate YAML data by comparing the data against a set of instructions.
    Any violations will be collected and returned in a `deque`

    Args:
        yaml_data (dict): The YAML data to validate. Assumes the YAML
            contains a root key
        instructions (dict): Contains the enums and rulesets that will be
            used to validate the YAML data

    Returns:
        deque: The violations that were detected in the data.

    Raises:
        ValueError: When the parameters `yaml_data` or `instructions` are `None`
    """
    if yaml_data is None:
        raise ValueError('yaml_data should not be None')

    if instructions is None:
        raise ValueError('instructions should not be None')

    default_key = '-'
    violations = deque()

    validators = _create_validators_chain(instructions, violations)
    validators.validate(default_key, yaml_data, default_key, None)

    return violations


def _create_validators_chain(instructions: dict,
                             violations: deque) -> Validator:
    ruleset_lookups = instructions.get('rules', {})
    enum_looksups = instructions.get('enums', {})
    entry_point = instructions.get('main', YamlatorRuleset('main', []))

    root = EntryPointValidator(violations, entry_point)
    optional_validator = OptionalValidator(violations)
    any_type_validator = AnyTypeValidator(violations)
    required_validator = RequiredValidator(violations)
    map_validator = MapValidator(violations)
    ruleset_validator = RulesetValidator(violations, ruleset_lookups)
    list_validator = ListValidator(violations)
    enum_validator = EnumTypeValidator(violations, enum_looksups)
    type_validator = BuiltInTypeValidator(violations)
    regex_validator = RegexValidator(violations)
    union_validator = UnionValidator(violations)

    root.set_next_validator(optional_validator)
    optional_validator.set_next_validator(required_validator)
    required_validator.set_next_validator(map_validator)
    map_validator.set_next_validator(ruleset_validator)

    ruleset_validator.set_next_ruleset_validator(optional_validator)
    ruleset_validator.set_next_validator(list_validator)

    list_validator.set_ruleset_validator(ruleset_validator)
    list_validator.set_next_validator(enum_validator)

    enum_validator.set_next_validator(any_type_validator)
    any_type_validator.set_next_validator(regex_validator)
    regex_validator.set_next_validator(type_validator)

    type_validator.set_next_validator(union_validator)

    union_validator.set_list_validator(list_validator)
    union_validator.set_ruleset_validator(ruleset_validator)
    union_validator.set_regex_validator(regex_validator)
    union_validator.set_enum_validator(enum_validator)
    union_validator.set_map_validator(map_validator)

    return root
