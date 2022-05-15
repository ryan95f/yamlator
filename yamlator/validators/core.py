from collections import deque
from typing import Iterable

from yamlator.types import Data
from yamlator.types import Rule
from yamlator.types import YamlatorRuleset

from .any_type_validator import AnyTypeValidator
from .base_validator import Validator
from .builtin_type_validator import BuiltInTypeValidator
from .enum_type_validator import EnumTypeValidator
from .list_validator import ListValidator
from .map_validator import MapValidator
from .optional_validator import OptionalValidator
from .regex_validator import RegexValidator
from .required_validator import RequiredValidator
from .ruleset_validator import RulesetValidator


def validate_yaml(yaml_data: Data, instructions: dict) -> deque:
    """Validate YAML data by comparing the data against a set of instructions.
    Any violations will be collected and returned in a `deque`

    Args:
        yaml_data (dict | list | int | float | str): The yaml data to validate

        instructions                         (dict): The instructions containing
        enums and rulesets that will be validated

    Returns:
        A deque with the violations that were detected in the data.

    Raises:
        ValueError if the parameters `yaml_data` or `instructions` are `None`.
    """
    if yaml_data is None:
        raise ValueError('yaml_data should not be None')

    if instructions is None:
        raise ValueError('instructions should not be None')

    entry_parent = '-'
    violations = deque()
    entry_point: YamlatorRuleset = instructions.get('main', YamlatorRuleset('main', []))

    validators = _create_validators_chain(
        ruleset_lookups=instructions.get('rules', {}),
        enum_looksups=instructions.get('enums', {}),
        violations=violations
    )

    entry_point_rules: Iterable[Rule] = entry_point.rules
    for rule in entry_point_rules:
        sub_data = yaml_data.get(rule.name, None)

        validators.validate(
            key=rule.name,
            data=sub_data,
            parent=entry_parent,
            rtype=rule.rtype,
            is_required=rule.is_required
        )

    return violations


def _create_validators_chain(ruleset_lookups: dict,
                             enum_looksups: dict,
                             violations: deque) -> Validator:

    root = OptionalValidator(violations)
    any_type_validator = AnyTypeValidator(violations)
    required_validator = RequiredValidator(violations)
    map_validator = MapValidator(violations)
    ruleset_validator = RulesetValidator(violations, ruleset_lookups)
    list_validator = ListValidator(violations)
    enum_validator = EnumTypeValidator(violations, enum_looksups)
    type_validator = BuiltInTypeValidator(violations)
    regex_validator = RegexValidator(violations)

    root.set_next_validator(required_validator)
    required_validator.set_next_validator(map_validator)
    map_validator.set_next_validator(ruleset_validator)

    ruleset_validator.set_next_ruleset_validator(root)
    ruleset_validator.set_next_validator(list_validator)

    list_validator.set_ruleset_validator(ruleset_validator)
    list_validator.set_next_validator(enum_validator)

    enum_validator.set_next_validator(any_type_validator)
    any_type_validator.set_next_validator(regex_validator)
    regex_validator.set_next_validator(type_validator)
    return root
