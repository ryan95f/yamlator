from __future__ import annotations
from turtle import rt
from typing import Iterable
from collections import deque
from abc import ABC, abstractmethod

from yamler.violations import RequiredViolation
from yamler.violations import RulesetTypeViolation
from yamler.violations import TypeViolation
from yamler.violations import ViolationManager


from .types import Data, Rule, RuleType


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
    """Wrangler for handling optional rules"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data to find any optional rules. If an optional rule is
        found and is None, then the next stage in the chain is not called otherwise
        it will be called.

        Args:
            key         (str): The key that owns the data
            data        (Data): The data to wrangler
            parent      (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool): Os the rule required
        """

        missing_data = data is None
        if not is_required and missing_data:
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RequiredWrangler(Wrangler):
    """Wrangler for handling data that is required"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data for required fields. If a required value
        is None, then it is added to the violation manager.

        Args:
            key         (str): The key that owns the data
            data        (Data): The data to wrangler
            parent      (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool): Os the rule required
        """

        missing_data = data is None
        if is_required and missing_data:
            violation = RequiredViolation(key, parent)
            self._violation_manager.add_violation(violation)
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RuleSetWrangler(Wrangler):
    """Wrangler for handling rulesets"""

    _ruleset_wrangler: Wrangler = None

    def __init__(self, violation_manager: ViolationManager, instructions: dict):
        """RuleSetWrangler Constructor

        Args:
            violation_manager (ViolationManager):   Violation manager
            instructions (dict):                    A dict container references to
            other rulesets
        """
        self.instructions = instructions
        super().__init__(violation_manager)

    def set_next_ruleset_wrangler(self, wrangler: Wrangler) -> None:
        """Set the next wrangler for handling nested rulesets in the data

        Args:
            wrangler (Wrangler): The wrangler to add to the chain
        """
        self._ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):
        """Wrangle the data rulesets and call the chain on the data itself to validate it.
        If the current rule is not a ruleset then the next wrangler is called
        in the chain. If the data is not in a dict format then a type violation is added.

        Args:
            key         (str): The key that owns the data
            data        (Data): The data to wrangler
            parent      (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool): Os the rule required
        """

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

            if self._ruleset_wrangler is not None:
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
    """Wrangler for handling list types"""

    ruleset_wrangler: Wrangler = None

    def set_ruleset_wrangler(self, wrangler: Wrangler) -> None:
        """Set a wrangler for when nested rulesets are within the list

        Args:
            wrangler (Wrangler): The wrangler to handle rulesets
        """
        self.ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the list data. If there is nested lists then this method
        will be recursively called. Any rulesets that are within the list will
        be handled by an additional wrangler that can be set with `set_ruleset_wrangler`.
        Any data type that is not a list is sent to the next wrangler.

        Args:
            key         (str): The key that owns the data
            data        (Data): The data to wrangler
            parent      (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool): Os the rule required
        """
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
        has_ruleset_wrangler = self.ruleset_wrangler is not None
        is_ruleset_rule = rtype.type == 'ruleset'

        if has_ruleset_wrangler and is_ruleset_rule:
            self.ruleset_wrangler.wrangle(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )


class BuildInTypeWrangler(Wrangler):
    """Wrangler to handle the build in types. e.g `int`, `list` & `str`"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data to valid its data type. If the data matches
        the rule, then it is passed onto the next stage in the chain otherwise
        a `TypeViolation` is added to the violation manager.

        Args:
            key         (str): The key that owns the data
            data        (Data): The data to wrangler
            parent      (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool): Os the rule required
        """

        if type(data) == rtype.type:
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if rtype.type != 'ruleset':
            message = f"{key} should be of type {rtype.type.__name__}"
            violation = TypeViolation(key, parent, message)
            self._violation_manager.add_violation(violation)
        else:
            super().wrangle(key, data, parent, rtype, is_required)
