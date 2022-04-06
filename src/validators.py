from __future__ import annotations
from typing import Iterable
from collections import deque, namedtuple

from src.violations import RequiredViolation
from src.violations import RulesetTypeViolation
from src.violations import TypeViolation

from src.types import Data
from src.types import Rule
from src.types import RuleType
from src.types import YamlatorRuleset
from src.types import SchemaTypes


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
    type_validator = BuildInTypeValidator(violations)

    root.set_next_validator(required_validator)
    required_validator.set_next_validator(map_validator)
    map_validator.set_next_validator(ruleset_validator)

    ruleset_validator.set_next_ruleset_validator(root)
    ruleset_validator.set_next_validator(list_validator)

    list_validator.set_ruleset_validator(ruleset_validator)
    list_validator.set_next_validator(enum_validator)

    enum_validator.set_next_validator(any_type_validator)
    any_type_validator.set_next_validator(type_validator)
    return root


class Validator:
    """Base class for validating a rule against the data"""

    _next_validator = None

    def __init__(self, violations: deque) -> None:
        """Validator init

        Args:
            violations (deque): Contains violations that have been detected
            whilst processing the data
        """
        self._violations = violations

    def set_next_validator(self, validator: Validator) -> Validator:
        """Set the next validator in the chain

        Args:
            validator (Validator): The next validator in the chain

        Returns:
            The object that was provided in the `validator` parameter
        """
        self._next_validator = validator
        return validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data against the next validator in the chain

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        if self._next_validator is not None:
            self._next_validator.validate(
                key=key,
                data=data,
                parent=parent,
                rtype=rtype,
                is_required=is_required
            )


class OptionalValidator(Validator):
    """Validator for handling optional rules"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate a key is an optional.

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        missing_data = data is None
        if not is_required and missing_data:
            return

        super().validate(key, data, parent, rtype, is_required)


class RequiredValidator(Validator):
    """Validator for handling data that is required"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate a key is a required rule

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        missing_data = data is None
        if is_required and missing_data:
            violation = RequiredViolation(key, parent)
            self._violations.append(violation)
            return

        super().validate(key, data, parent, rtype, is_required)


class RulesetValidator(Validator):
    """Validator for handling rulesets"""

    _ruleset_validator: Validator = None

    def __init__(self, violations: deque, instructions: dict):
        """RulesetValidator init

        Args:
            violations  (deque):  Contains violations that have been detected
            whilst processing the data

            instructions (dict): A dict containing references to other rulesets
        """
        self.instructions = instructions
        super().__init__(violations)

    def set_next_ruleset_validator(self, validator: Validator) -> None:
        """Set the next validator for handling nested rulesets

        Args:
            validator (Validator): The ruleset validator
        """
        self._ruleset_validator = validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False):
        """Validate the data against a ruleset

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        is_ruleset_rule = (rtype.type == SchemaTypes.RULESET)
        if not is_ruleset_rule:
            super().validate(key, data, parent, rtype, is_required)
            return

        is_ruleset_data = (type(data) == dict)
        if not is_ruleset_data:
            violation = RulesetTypeViolation(key, parent)
            self._violations.append(violation)
            return

        ruleset_rules = self._retrieve_next_ruleset(rtype.lookup)

        for ruleset_rule in ruleset_rules:
            sub_data = data.get(ruleset_rule.name, None)

            if self._ruleset_validator is not None:
                self._ruleset_validator.validate(
                    key=ruleset_rule.name,
                    data=sub_data,
                    parent=key,
                    rtype=ruleset_rule.rtype,
                    is_required=ruleset_rule.is_required
                )

    def _retrieve_next_ruleset(self, ruleset_name: str) -> Iterable[Rule]:
        default_missing_ruleset = YamlatorRuleset(ruleset_name, [])
        ruleset = self.instructions.get(ruleset_name, default_missing_ruleset)
        return ruleset.rules


class ListValidator(Validator):
    """Validtor for handling list types"""

    ruleset_validator: Validator = None

    def set_ruleset_validator(self, validator: Validator) -> None:
        """Set a validator for when nested rulesets are within the list

        Args:
            validator (Validator): The validator to handle rulesets
        """
        self.ruleset_validator = validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the list data. This validator will recursive if
        nested lists are detected in the rule

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        is_list_rule = (rtype.type == SchemaTypes.LIST)
        is_list_data = (type(data) != list)

        if not is_list_rule or is_list_data:
            super().validate(key, data, parent, rtype, is_required)
            return

        for idx, item in enumerate(data):
            current_key = f"{key}[{idx}]"

            # loop over any nested lists
            self.validate(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

            # a list could contain ruleset items
            # so need to run each item through that validator
            self._run_ruleset_validator(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

    def _run_ruleset_validator(self, key: str, parent: str, data: Data, rtype: RuleType):
        has_ruleset_validator = (self.ruleset_validator is not None)
        is_ruleset_rule = (rtype.type == SchemaTypes.RULESET)

        if has_ruleset_validator and is_ruleset_rule:
            self.ruleset_validator.validate(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )


_SchemaTypeDecoder = namedtuple("SchemaTypeDecoder", ["type", "friendly_name"])


class BuildInTypeValidator(Validator):
    """Validator to handle the build in types. e.g `int`, `list` & `str`"""

    def __init__(self, violations: deque) -> None:
        """BuildInTypeValidator init

        Args:
            violations (deque): Contains violations that have been detected
            whilst processing the data
        """
        super().__init__(violations)
        self._built_in_lookups = {
            SchemaTypes.INT: _SchemaTypeDecoder(int, "int"),
            SchemaTypes.STR: _SchemaTypeDecoder(str, "str"),
            SchemaTypes.FLOAT: _SchemaTypeDecoder(float, "float"),
            SchemaTypes.LIST: _SchemaTypeDecoder(list, "list"),
            SchemaTypes.MAP: _SchemaTypeDecoder(dict, "map"),
        }

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data against the core base types. If the data
        does not match the expected type, then a `TypeViolation` is added
        to the list of violations

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        buildin_type = self._built_in_lookups.get(rtype.type)
        is_not_build_in_type = (buildin_type is None)
        if is_not_build_in_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        if type(data) != buildin_type.type:
            message = f'{key} should be of type {buildin_type.friendly_name}'
            violation = TypeViolation(key, parent, message)
            self._violations.append(violation)
            return

        super().validate(key, data, parent, rtype, is_required)


class MapValidator(Validator):
    """Validator to handle map types"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data contained within in a map

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        is_map_rule = (rtype.type == SchemaTypes.MAP)
        is_map_data = (type(data) == dict)

        if not is_map_rule or not is_map_data:
            super().validate(key, data, parent, rtype, is_required)
            return

        for child_key, value in data.items():
            self.validate(
                key=child_key,
                data=value,
                parent=key,
                rtype=rtype.sub_type)


class AnyTypeValidator(Validator):
    """Validator to handle the `any` type. This type ignores all type checks"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate any rules that have the data marked as the `any` type

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        is_any_type = (rtype.type == SchemaTypes.ANY)
        if is_any_type:
            return

        super().validate(key, data, parent, rtype, is_required)


class EnumTypeValidator(Validator):
    """Validator to handle data that is contained in a enum"""

    def __init__(self, violations: deque, enums: dict):
        """EnumTypeValidator init

        Args:
            violations (deque): Contains violations that have been detected
            whilst processing the data

            enums       (dict): A dict that contains references to enums
            referenced in the rulesets.
        """
        super().__init__(violations)
        self.enums = enums

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate enum data. If the data does not align to a know value
        in the enum, then a `TypeViolation` is added to the violation list

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        is_enum_type = (rtype.type == SchemaTypes.ENUM)
        if not is_enum_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        is_enum_str_data = isinstance(data, str)
        if not is_enum_str_data:
            self._add_enum_violation(key, parent, rtype.lookup)
            return

        if self._matches_enum_data(data, rtype.lookup):
            return

        self._add_enum_violation(key, parent, rtype.lookup)

    def _matches_enum_data(self, data: Data, enum_name: str) -> bool:
        target_enum = self.enums.get(enum_name, None)

        if target_enum is None:
            return False

        enum_value = target_enum.items.get(data, None)
        return enum_value is not None

    def _add_enum_violation(self, key: str, parent: str, enum_name: str):
        message = f'{key} does not match any value in enum {enum_name}'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)
