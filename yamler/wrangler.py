from enum import Enum
from typing import Iterable
from collections import deque

from .types import Rule, Data, RuleType


class YamlerWrangler:
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

    def wrangle(self, yaml_data: dict) -> deque:
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

        self.violations = deque()
        main_rules = self._main.get('rules', [])
        self._wrangle("-", yaml_data, main_rules)
        return self.violations

    def _wrangle(self, parent: str, data: dict, rules: Iterable[Rule]) -> None:
        for rule in rules:
            sub_data = data.get(rule.name, None)

            if self._is_optional_missing_data(sub_data, rule):
                continue

            if self._is_required_missing_data(sub_data, rule):
                violation_type = RequiredViolation(key=rule.name, parent=parent)
                self.violations.append(violation_type)
                continue

            if self._is_ruleset_rule(rule.rtype):
                self._wrangler_ruleset(rule.name, sub_data, rule.rtype)
                continue

            if self._is_list_rule(rule.rtype):
                self._wrangle_lists(parent, rule.name, sub_data, rule.rtype.sub_type)
                continue

            if self._has_incorrect_type(sub_data, rule.rtype):
                self._resolve_incorrect_type(rule.name, parent, rule.rtype.type)
                continue

    def _is_optional_missing_data(self, data: Data, rule: Rule) -> bool:
        return (not rule.is_required) and (data is None)

    def _is_required_missing_data(self, data: Data, rule: Rule) -> bool:
        return (rule.is_required) and (data is None)

    def _is_ruleset_rule(self, rtype: RuleType) -> bool:
        return rtype.type == 'ruleset'

    def _is_dict_type(self, data: Data) -> bool:
        return type(data) == dict

    def _wrangler_ruleset(self, key: str, data: Data, rtype: RuleType) -> None:
        if not self._is_dict_type(data):
            violation_type = RulesetTypeViolation(key=key, parent=key)
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
                self._resolve_incorrect_type(current_key, parent, rtype.type)
                continue

            if self._is_list_rule(rtype):
                self._wrangle_lists(current_key, current_key, item, rtype.sub_type)
                continue

    def _has_incorrect_type(self, data: Data, rtype: RuleType) -> bool:
        return type(data) != rtype.type

    def _resolve_incorrect_type(self, key: str, parent: str, expected_type: type) -> None:
        violation_type = BuiltInTypeViolation(key, parent, expected_type)
        self.violations.append(violation_type)


class ViolationType(Enum):
    REQUIRED = "required"
    TYPE = "type"


class Violation:
    def __init__(self, key: str, parent: str, message: str, v_type: ViolationType):
        """Violation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
            message (str):  The message with information regarding the violation
            v_type  (str):  The violation type. Either `REQUIRED` or `TYPE`
        """
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
    """Violation for when a required field is missing"""

    def __init__(self, key: str, parent: str):
        """RequiredViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
        """
        message = f"{key} is required"
        super().__init__(key, parent, message, ViolationType.REQUIRED)


class TypeViolation(Violation):
    """Violation when a value in the YAML file has an incorrect type"""

    def __init__(self, key: str, parent: str, message: str):
        """TypeViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
            message (str):  The message with information regarding the type violation
        """
        super().__init__(key, parent, message, ViolationType.TYPE)


class BuiltInTypeViolation(TypeViolation):
    """Type violation when a field is not using the required
    built in type e.g (float, int, str, list)
    """

    def __init__(self, key: str, parent: str, expected_type: type):
        """BuiltInTypeViolation constructor

        Args:
            key             (str):  The key name in the YAML file
            parent          (str):  The parent key in the YAML file
            expected_type   (type): The expected build in type for the field
        """
        message = f"{key} is expected to be an {expected_type.__name__}"
        super().__init__(key, parent, message)


class RulesetTypeViolation(TypeViolation):
    """Type violation when a field is not a ruleset (dict) in the file"""

    def __init__(self, key: str, parent: str):
        """RulesetTypeViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
        """
        message = f"{key} should be a ruleset"
        super().__init__(key, parent, message)
