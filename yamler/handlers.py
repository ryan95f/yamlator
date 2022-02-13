from __future__ import annotations
from typing import Iterable
from collections import deque
from abc import ABC, abstractmethod

from yamler.wrangler import RequiredViolation
from yamler.wrangler import RulesetTypeViolation
from yamler.wrangler import TypeViolation
from yamler.wrangler import Violation


from .types import Data, Rule, RuleType


class ViolationManager:
    def __init__(self):
        self._violations = deque()

    @property
    def violations(self):
        return self._violations.copy()

    def add_violation(self, violation: Violation):
        self._violations.append(violation)

    def clear(self):
        self._violations.clear()


class ChianWrangler:
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

        self._violation_manager = ViolationManager()

        self.root = OptionalWrangler(self._violation_manager)
        required_wrangler = RequiredWrangler(self._violation_manager)
        ruleset_wrangler = RuleSetWrangler(self._violation_manager, self._instructions)
        list_wrangler = ListWrangler(self._violation_manager)
        type_wrangler = BuildInTypeWrangler(self._violation_manager)

        self.root.set_next_wrangler(required_wrangler)
        required_wrangler.set_next_wrangler(ruleset_wrangler)
        ruleset_wrangler.set_next_ruleset_wrangler(self.root)
        ruleset_wrangler.set_next_wrangler(list_wrangler)
        list_wrangler.set_ruleset_wrangler(ruleset_wrangler)
        list_wrangler.set_next_wrangler(type_wrangler)

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

        self._violation_manager.clear()
        main_rules = self._main.get('rules', [])
        self._wrangle("-", yaml_data, main_rules)
        return self._violation_manager.violations

    def _wrangle(self, parent: str, data: dict, rules: Iterable[Rule]) -> None:
        for rule in rules:
            sub_data = data.get(rule.name, None)
            self.root.wrangle(rule.name, sub_data, parent, rule.rtype, rule.is_required)


class Wrangler(ABC):
    _next_wrangler = None

    def __init__(self, violation_manager: ViolationManager) -> None:
        self._violation_manager = violation_manager

    def set_next_wrangler(self, wrangler: Wrangler) -> Wrangler:
        self._next_wrangler = wrangler
        return wrangler

    @abstractmethod
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        if self._next_wrangler is not None:
            self._next_wrangler.wrangle(
                key=key,
                data=data,
                parent=parent,
                rtype=rtype,
                is_required=is_required
            )


class OptionalWrangler(Wrangler):
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        missing_data = data is None
        if not is_required and missing_data:
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RequiredWrangler(Wrangler):
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        missing_data = data is None
        if is_required and missing_data:
            violation = RequiredViolation(key, parent)
            self._violation_manager.add_violation(violation)
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RuleSetWrangler(Wrangler):
    def __init__(self, violation_manager: ViolationManager, instructions: dict):
        self.instructions = instructions
        super().__init__(violation_manager)

    def set_next_ruleset_wrangler(self, wrangler: Wrangler):
        self._ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        if not self._is_ruleset_rule(rtype):
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if not self._is_ruleset(data):
            violation = RulesetTypeViolation(key, parent)
            self._violation_manager.add_violation(violation)
            return

        ruleset_lookup_name = rtype.lookup
        ruleset = self.instructions['rules'].get(ruleset_lookup_name, {})
        ruleset_rules: Iterable[Rule] = ruleset['rules']

        for ruleset_rule in ruleset_rules:
            sub_data = data.get(ruleset_rule.name, None)
            self._ruleset_wrangler.wrangle(
                key=ruleset_rule.name,
                data=sub_data,
                parent=key,
                rtype=ruleset_rule.rtype,
                is_required=ruleset_rule.is_required
            )

    def _is_ruleset_rule(self, rtype) -> bool:
        return rtype.type == 'ruleset'

    def _is_ruleset(self, data):
        return type(data) == dict


class ListWrangler(Wrangler):
    ruleset_wrangler: Wrangler = None

    def set_ruleset_wrangler(self, wrangler: Wrangler):
        self.ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        if not self._is_list_rule(rtype):
            super().wrangle(key, data, parent, rtype, is_required)
            return

        for idx, item in enumerate(data):
            current_key = f"{key}[{idx}]"

            # loop over any nested lists
            self.wrangle(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

            if self.ruleset_wrangler is not None:
                self.ruleset_wrangler.wrangle(
                    key=current_key,
                    parent=key,
                    data=item,
                    rtype=rtype.sub_type
                )

    def _is_list_rule(self, rtype: RuleType):
        return rtype.type == list


class BuildInTypeWrangler(Wrangler):
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):

        if type(data) == rtype.type:
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if rtype.type != 'ruleset':
            message = f"{key} should be of type {rtype.type}"
            violation = TypeViolation(key, parent, message)
            self._violation_manager.add_violation(violation)
