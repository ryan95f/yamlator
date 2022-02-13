from __future__ import annotations
from typing import Iterable
from collections import deque
from abc import ABC, abstractmethod

from yamler.violations import RequiredViolation
from yamler.violations import RulesetTypeViolation
from yamler.violations import TypeViolation
from yamler.violations import Violation


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


def wrangle_data(yaml_data: dict, instructions: dict) -> deque:
    entry_parent = "-"
    violation_mgnr = ViolationManager()
    entry_point = instructions.get('main', {})

    wranglers = _create_wrangler_chain(
        instructions=instructions,
        violation_manager=violation_mgnr
    )

    entry_point_rules: Iterable[Rule] = entry_point.get('rules', [])
    for rule in entry_point_rules:
        sub_data = yaml_data.get(rule.name, None)

        wranglers.wrangle(
            key=rule.name,
            data=sub_data,
            parent=entry_parent,
            rtype=rule.rtype,
            is_required=rule.is_required
        )

    return violation_mgnr.violations


def _create_wrangler_chain(instructions: dict,
                           violation_manager: ViolationManager) -> Wrangler:

    root = OptionalWrangler(violation_manager)
    required_wrangler = RequiredWrangler(violation_manager)
    ruleset_wrangler = RuleSetWrangler(violation_manager, instructions)
    list_wrangler = ListWrangler(violation_manager)
    type_wrangler = BuildInTypeWrangler(violation_manager)

    root.set_next_wrangler(required_wrangler)
    required_wrangler.set_next_wrangler(ruleset_wrangler)
    ruleset_wrangler.set_next_ruleset_wrangler(root)
    ruleset_wrangler.set_next_wrangler(list_wrangler)
    list_wrangler.set_ruleset_wrangler(ruleset_wrangler)
    list_wrangler.set_next_wrangler(type_wrangler)

    return root


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

        ruleset_rules = self._retrieve_next_ruleset(rtype.lookup)

        for ruleset_rule in ruleset_rules:
            sub_data = data.get(ruleset_rule.name, None)
            self._ruleset_wrangler.wrangle(
                key=ruleset_rule.name,
                data=sub_data,
                parent=key,
                rtype=ruleset_rule.rtype,
                is_required=ruleset_rule.is_required
            )

    def _is_ruleset_rule(self, rtype: RuleType) -> bool:
        return rtype.type == 'ruleset'

    def _is_ruleset(self, data: Data) -> bool:
        return type(data) == dict

    def _retrieve_next_ruleset(self, ruleset_name: str) -> Iterable[Rule]:
        ruleset = self.instructions['rules'].get(ruleset_name, {})
        return ruleset.get('rules', [])


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

            # a list could contain ruleset items
            # so need to run each item through that wrangler
            self._run_ruleset_wrangler(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

    def _is_list_rule(self, rtype: RuleType):
        return rtype.type == list

    def _run_ruleset_wrangler(self, key: str, parent: str, data: Data, rtype: RuleType):
        if self.ruleset_wrangler is not None:
            self.ruleset_wrangler.wrangle(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )


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
