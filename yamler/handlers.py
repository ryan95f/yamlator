from typing import Iterable
from collections import deque
from abc import ABC, abstractmethod

from .types import Rule


class Handler(ABC):
    next: 'Handler' = None

    def set_next(self, next: 'Handler') -> 'Handler':
        self.next = next
        return next

    @abstractmethod
    def validate(self, key, data, parent, rule: Rule) -> None:
        pass


class OptionalFieldHandler(Handler):
    def validate(self, key, data, parent, rule: Rule) -> None:
        is_optional = not rule.is_required

        if is_optional and (data is None):
            return

        if self.next is not None:
            self.next.validate(key, data, parent, rule)


class RequiredFieldHandler(Handler):
    def validate(self, key, data, parent, rule: Rule) -> None:
        is_required = rule.is_required
        if is_required and (data is None):
            print(f"{key} is required")
            return

        if self.next is not None:
            self.next.validate(key, data, parent, rule)


class RuleSetTypeHandler(Handler):
    def __init__(self, instructions: dict) -> None:
        self.instructions = instructions
        self._next_ruleset = None

    def set_next_ruleset(self, next: Handler) -> Handler:
        self._next_ruleset = next
        return next

    def validate(self, key, data, parent, rule: Rule) -> None:
        if self._is_ruleset_rule(rule.rtype) and self._is_ruleset(data):
            lookup_name = rule.rtype.lookup
            ruleset = self.instructions['rules'].get(lookup_name, {})
            
            rules: Iterable[Rule] = ruleset['rules']
            for r_rule in rules:
                sub_data = data.get(r_rule.name, None)
                self._next_ruleset.validate(r_rule.name, sub_data, key, r_rule)

        if self.next is not None:
            self.next.validate(key, data, parent, rule)

    def _is_ruleset_rule(self, rtype) -> bool:
        return rtype.type == 'ruleset'

    def _is_ruleset(self, data):
        return type(data) == dict


class ListTypeHandler(Handler):
    def validate(self, key, data, parent, rule: Rule) -> None:
        if rule.rtype.type == list:
            for idx, item in enumerate(data):
                print(item, rule)

        if self.next is not None:
            self.next.validate()


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

        self.root = OptionalFieldHandler()
        required_handler = self.root.set_next(RequiredFieldHandler())
        ruleset_handler = required_handler.set_next(RuleSetTypeHandler(self._instructions))
        ruleset_handler.set_next_ruleset(self.root)
        list_handler = ruleset_handler.set_next(ListTypeHandler())

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
            self.root.validate(rule.name, sub_data, parent, rule)
