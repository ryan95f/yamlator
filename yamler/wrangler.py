from enum import Enum
from typing import Iterable

from .types import Rule


class ViolationType(Enum):
    REQUIRED = "required"
    TYPE = "type"


class Violation:
    def __init__(self, key: str, parent: str, message: str,
                 v_type: ViolationType):
        self._key = key
        self._message = message
        self._parent = parent
        self._v_type = v_type

    @property
    def key(self):
        return self._key

    @property
    def message(self):
        return self._message

    @property
    def violation_type(self):
        return self._v_type.value

    @property
    def parent(self):
        if len(self._parent) == 0:
            return "-"
        return self._parent

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


class RulesetTypeViolation(TypeViolation):
    def __init__(self, key: str, parent: str):
        message = f"{key} should be a ruleset"
        super().__init__(key, parent, message)

# class YamlerWrangler:
#     """Reads the instructions from the parser to validate if a
#     YAML file meets the define rules
#     """

#     def __init__(self, instructions: dict):
#         """YamlerWrangler constructor

#         Args:
#             instructions (dict): Contains the main ruleset and a list of
#                                  other rulesets

#         Raises:
#             ValueError: If instructions is None
#         """
#         if instructions is None:
#             raise ValueError("instructions should not be None")

#         self._instructions = instructions
#         self._main = instructions.get('main', {})

#     def wrangle(self, yaml_data: dict) -> dict:
#         """Wrangle the YAML file to determine if there are any
#         violations when compared to the rulesets

#         Args:
#             yaml_data (dict): The yaml data represented as a dict

#         Returns:
#             A `dict` of violations that were detected

#         Raises:
#             ValueError: If `yaml_data` is None
#         """
#         if yaml_data is None:
#             raise ValueError("yaml_data should not be None")

#         self.violations = {}
#         main_rules = self._main.get('rules', [])
#         self._wrangle(yaml_data, main_rules)
#         return self.violations

#     def _wrangle(self, data: dict, rules: list, parent: str = ""):
#         for rule in rules:
#             name = rule.get('name')
#             rtype = rule.get('rtype')

#             sub_data = data.get(name, None)
#             if self.is_optional_field_missing(sub_data, rule):
#                 continue

#             if self._is_missing_required_data(sub_data, rule):
#                 msg = f"{name} is missing"
#                 violation = RequiredViolation(name, parent, msg)
#                 self._update_violation(f"{parent}#{name}", violation)
#                 continue

#             if self._is_ruleset_rule(rule):
#                 self._wrangle_rulesets(parent, name, sub_data, rule)
#                 continue

#             if self._has_incorrect_type(sub_data, rule):
#                 msg = f"{name} should be type({rtype['type'].__name__})"
#                 violation = TypeViolation(name, parent, msg)
#                 self._update_violation(f"{parent}#{name}", violation)
#                 continue

#             if rtype['type'] == list:
#                 self._wrangle_lists(parent, name, sub_data, rtype)
#                 continue

#         return self.violations

#     def is_optional_field_missing(self, data, rule: Rule):
#         return (rule.is_required) and (data is None)

#     def _is_missing_required_data(self, data, rule: Rule):
#         required = rule['required']
#         return required and data is None

#     def _is_ruleset_type(self, data):
#         return type(data) == dict

#     def _update_violation(self, name: str, violation: Violation):
#         self.violations[name] = violation

#     def _is_ruleset_rule(self, rule):
#         rtype = rule['rtype']
#         return rtype['type'] == 'ruleset'

#     def _wrangle_rulesets(self, parent, name, data, rule):
#         rtype = rule.get('rtype')
#         if self._is_ruleset_type(data):
#             ruleset_name = rtype['lookup']
#             ruleset = self._instructions['rules'].get(ruleset_name)
#             self._wrangle(data, ruleset['rules'], name)
#             return

#         # Ignore optional rulesets
#         required = rule.get('required', True)
#         if not required and data is None:
#             return

#         msg = f"{name} should be type(ruleset)"
#         violation = TypeViolation(parent, name, msg)
#         self._update_violation(f"{parent}#{name}", violation)

#     def _has_incorrect_type(self, data, rule: dict):
#         rtype = rule['rtype']
#         return (type(data) != rtype['type']) and (data is not None)

#     def _wrangle_lists(self, parent, name, data, rtype):
#         list_type = rtype['sub_type']
#         for i, item in enumerate(data):
#             if list_type['type'] == 'ruleset':
#                 lookup = list_type['lookup']
#                 ruleset = self._instructions['rules'].get(lookup, {})
#                 if not self._is_ruleset_type(item):
#                     msg = f"{name}[{i}] should be type(ruleset)"
#                     violation = TypeViolation(parent, name, msg)
#                     self._update_violation(f"{parent}#{name}[{i}]", violation)
#                     continue
#                 self._wrangle(item, ruleset['rules'], f"{name}[{i}]")
#                 continue

#             if type(item) != list_type['type']:
#                 msg = f"{name}[{i}] should be {list_type['type'].__name__}"
#                 violation = TypeViolation(f"{name}[{i}]", parent, msg)
#                 self._update_violation(f"{parent}#{name}[{i}]", violation)
#                 continue

#             if list_type['type'] == list:
#                 parent_list = f"{name}[{i}]"
#                 list_name = f"{name}[{i}]"
#                 self._wrangle_lists(parent_list,
#                                     list_name,
#                                     item,
#                                     rtype['sub_type'])


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

    def _wrangle(self, parent: str, data: dict, rules: Iterable[Rule]):
        for rule in rules:
            sub_data = data.get(rule.name, None)

            if self._is_optional_missing_data(sub_data, rule):
                continue

            if self._is_required_missing_data(sub_data, rule):
                violation_type = RequiredViolation(rule.name, parent)
                self.violations.append(violation_type)
                continue

            if self._is_ruleset_rule(rule):
                if type(sub_data) != dict:
                    violation_type = RulesetTypeViolation(rule.name, parent)
                    self.violations.append(violation_type)
                    continue

                self._wrangle_ruleset(sub_data, rule)
                continue

            if self._is_list_rule(rule):
                self._wrangle_lists(parent, rule.name, sub_data, rule.rtype['sub_type'])
                continue

            if self._has_incorrect_type(sub_data, rule):
                violation_type = TypeViolation(key=rule.name, parent=parent, message=f"{rule.name} should be {rule.rtype['type'].__name__}")
                self.violations.append(violation_type)
                continue

    def _is_optional_missing_data(self, data, rule: Rule):
        return (not rule.is_required) and (data is None)

    def _is_required_missing_data(self, data, rule: Rule):
        return (rule.is_required) and (data is None)

    def _is_ruleset_rule(self, rule: Rule):
        rtype = rule.rtype
        return rtype['type'] == 'ruleset'

    def _wrangle_ruleset(self, data: dict, rule: Rule):
        rtype = rule.rtype
        lookup_name = rtype['lookup']
        ruleset = self._instructions['rules'].get(lookup_name, {})
        self._wrangle(rule.name, data, ruleset['rules'])

    def _is_list_rule(self, rule: Rule):
        rtype = rule.rtype
        return rtype['type'] == list

    def _wrangle_lists(self, parent, key, data, rtype):
        for idx, d in enumerate(data):
            if rtype['type'] == "ruleset":
                if type(d) != dict:
                    violation_type = RulesetTypeViolation(key=f"{key}[{idx}]", parent=parent)
                    self.violations.append(violation_type)
                    continue

                lookup_name = rtype['lookup']
                ruleset = self._instructions['rules'].get(lookup_name, {})
                self._wrangle(f"{key}[{idx}]", d, ruleset['rules'])
                continue

            if type(d) != rtype['type']:
                violation_type = TypeViolation(key=key, parent=parent, message=f"{key}[{idx}] should be {rtype['type'].__name__}")
                self.violations.append(violation_type)
                continue

            if rtype['type'] == list:
                self._wrangle_lists(f"{key}[{idx}]", f"{key}[{idx}]", d, rtype['sub_type'])
                continue

    def _has_incorrect_type(self, data, rule: Rule):
        rtype = rule.rtype
        return (type(data) != rtype['type'])
