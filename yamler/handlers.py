from typing import Iterable
from collections import deque
from abc import ABC, abstractmethod

from .types import Data, Rule, RuleType


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

        self.root = OptionalWrangler()
        required_wrangler = RequiredWrangler()
        ruleset_wrangler = RuleSetWrangler(self._instructions)
        list_wrangler = ListWrangler()

        self.root.set_next_wrangler(required_wrangler)
        required_wrangler.set_next_wrangler(ruleset_wrangler)
        ruleset_wrangler.set_next_ruleset_wrangler(self.root)
        ruleset_wrangler.set_next_wrangler(list_wrangler)
        list_wrangler.set_ruleset_wrangler(ruleset_wrangler)

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
            self.root.wrangle(rule.name, sub_data, parent, rule.rtype, rule.is_required)


class Wrangler(ABC):
    _next_wrangler = None

    def set_next_wrangler(self, wrangler: 'Wrangler') -> 'Wrangler':
        self._next_wrangler = wrangler
        return wrangler

    @abstractmethod
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType, required=False):
        pass


class OptionalWrangler(Wrangler):
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType, required=False):
        missing_data = data is None

        if not required and missing_data:
            return

        if self._next_wrangler is not None:
            self._next_wrangler.wrangle(key, data, parent, rtype, required)


class RequiredWrangler(Wrangler):
    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType, required=False):
        missing_data = data is None

        if required and missing_data:
            print(f"{key} is required")
            return

        if self._next_wrangler is not None:
            self._next_wrangler.wrangle(key, data, parent, rtype, required)


class RuleSetWrangler(Wrangler):
    def __init__(self, instructions: dict):
        self.instructions = instructions

    def set_next_ruleset_wrangler(self, wrangler: Wrangler):
        self._ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType, required=False):
        if self._is_ruleset_rule(rtype) and self._is_ruleset(data):
            lookup_name = rtype.lookup
            ruleset = self.instructions['rules'].get(lookup_name, {})

            rules: Iterable[Rule] = ruleset['rules']
            for r_rule in rules:
                sub_data = data.get(r_rule.name, None)
                self._ruleset_wrangler.wrangle(
                    key=r_rule.name,
                    data=sub_data,
                    parent=key,
                    rtype=r_rule.rtype,
                    required=r_rule.is_required
                )

        if self._next_wrangler is not None:
            self._next_wrangler.wrangle(key, data, parent, rtype, required)

    def _is_ruleset_rule(self, rtype) -> bool:
        return rtype.type == 'ruleset'

    def _is_ruleset(self, data):
        return type(data) == dict


class ListWrangler(Wrangler):
    def set_ruleset_wrangler(self, wrangler: Wrangler):
        self.ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType, required=False):
        if self._is_list_rule(rtype):
            for idx, item in enumerate(data):
                current_key = f"{key}[{idx}]"

                # loop over any nested lists
                self.wrangle(
                    key=current_key,
                    parent=current_key,
                    data=item,
                    rtype=rtype.sub_type
                )

                self.ruleset_wrangler.wrangle(
                    key=current_key,
                    parent=parent,
                    data=item,
                    rtype=rtype.sub_type
                )


    def _is_list_rule(self, rtype: RuleType):
        return rtype.type == list
