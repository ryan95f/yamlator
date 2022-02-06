from enum import Enum
from typing import Iterable

from .types import Rule, Data, RuleType


class ImprovedWrangler:
    def __init__(self, instructions: dict):
        """YamlerWrangler constructor

        Args:
            instructions (dict): Contains the main ruleset and a list of
                                 other rulesets

        Raises:
            ValueError: If instructions is None
        """
        if instructions is None:
            raise ValueError("instructions should not be None")

        self._instructions = instructions
        self._main = instructions.get('main', {})

    def wrangle(self, yaml_data: dict) -> dict:
        """Wrangle the YAML file to determine if there are any
        violations when compared to the rulesets

        Args:
            yaml_data (dict): The yaml data represented as a dict

        Returns:
            A `dict` of violations that were detected

        Raises:
            ValueError: If `yaml_data` is None
        """
        if yaml_data is None:
            raise ValueError("yaml_data should not be None")

        self.violations = []
        main_rules = self._main.get('rules', [])
        self._wrangle("-", yaml_data, main_rules)
        return self.violations

    def _wrangle(self, parent: str, data: dict, rules: Iterable[Rule]) -> None:
        for rule in rules:
            sub_data = data.get(rule.name, None)

            if self._is_optional_missing_data(sub_data, rule):
                continue

            if self._is_required_missing_data(sub_data, rule):
                violation_type = RequiredViolation(rule.name, parent)
                self.violations.append(violation_type)
                continue

            if self._is_ruleset_rule(rule.rtype):
                self._wrangler_ruleset(rule.name, sub_data, rule.rtype)
                continue

            if self._is_list_rule(rule.rtype):
                self._wrangle_lists(parent, rule.name, sub_data, rule.rtype.sub_type)
                continue

            if self._has_incorrect_type(sub_data, rule.rtype):
                violation_type = BuiltInTypeViolation(key=rule.name,
                                                      parent=parent,
                                                      expected_type=rule.rtype.type)
                self.violations.append(violation_type)
                continue

    def _is_optional_missing_data(self, data, rule: Rule) -> bool:
        return (not rule.is_required) and (data is None)

    def _is_required_missing_data(self, data, rule: Rule) -> bool:
        return (rule.is_required) and (data is None)

    def _is_ruleset_rule(self, rtype: RuleType) -> bool:
        return rtype.type == 'ruleset'

    def _is_dict_type(self, data: Data) -> bool:
        return type(data) == dict

    def _wrangler_ruleset(self, key: str, data: Data, rtype: RuleType) -> None:
        if not self._is_dict_type(data):
            violation_type = RulesetTypeViolation(key, key)
            self.violations.append(violation_type)
            return

        lookup_name = rtype.lookup
        ruleset = self._instructions['rules'].get(lookup_name, {})
        self._wrangle(key, data, ruleset['rules'])

    def _is_list_rule(self, rtype: RuleType) -> bool:
        return rtype.type == list

    def _wrangle_lists(self, parent: str, key: str, list_data: list,
                       rtype: RuleType) -> None:

        for idx, item in enumerate(list_data):
            current_key = f"{key}[{idx}]"

            if self._is_ruleset_rule(rtype):
                self._wrangler_ruleset(current_key, item, rtype)
                continue

            if self._has_incorrect_type(item, rtype):
                violation_type = BuiltInTypeViolation(key=current_key,
                                                      parent=parent,
                                                      expected_type=rtype.type)
                self.violations.append(violation_type)
                continue

            if self._is_list_rule(rtype):
                self._wrangle_lists(current_key, current_key, item, rtype.sub_type)
                continue

    def _has_incorrect_type(self, data: Data, rtype: RuleType) -> bool:
        return type(data) != rtype.type


class ViolationType(Enum):
    REQUIRED = "required"
    TYPE = "type"


class Violation:
    def __init__(self, key: str, parent: str, message: str, v_type: ViolationType):
        self.key = key
        self.message = message
        self.parent = parent
        self._violation_type = v_type

    @property
    def violation_type(self) -> str:
        return self._violation_type.value

    def __repr__(self) -> str:
        message_template = "{}(parent={}, key={}, message={}"
        return message_template.format(__class__.__name__,
                                       self.parent, self.key, self.message)


class RequiredViolation(Violation):
    def __init__(self, key: str, parent: str):
        message = f"{key} is required"
        super().__init__(key, parent, message, ViolationType.REQUIRED)


class TypeViolation(Violation):
    def __init__(self, key: str, parent: str, message: str):
        super().__init__(key, parent, message, ViolationType.TYPE)


class BuiltInTypeViolation(TypeViolation):
    def __init__(self, key: str, parent: str, expected_type: type):
        message = f"{key} is expected to be an {expected_type.__name__}"
        super().__init__(key, parent, message)


class RulesetTypeViolation(TypeViolation):
    def __init__(self, key: str, parent: str):
        message = f"{key} should be a ruleset"
        super().__init__(key, parent, message)
