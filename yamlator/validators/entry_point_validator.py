from collections import deque
from typing import Iterable

from yamlator.types import Data
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import YamlatorRuleset
from yamlator.violations import StrictEntryPointViolation
from .base_validator import Validator


class EntryPointValidator(Validator):

    def __init__(self, violations: deque, entry_point: YamlatorRuleset):
        self._entry_point = entry_point
        super().__init__(violations)

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        del key
        del rtype
        del is_required

        rules = self._entry_point.rules
        if self._entry_point.is_strict:
            self._handle_strict_mode(data, rules)

        for rule in rules:
            sub_data = data.get(rule.name, None)

            super().validate(rule.name, sub_data, parent,
                             rule.rtype, rule.is_required)

    def _handle_strict_mode(self, data: dict, rules: Iterable[Rule]):
        rule_fields = {rule.name for rule in rules}
        data_fields = set(data.keys())
        extra_fields = data_fields - rule_fields

        for field in extra_fields:
            violation = StrictEntryPointViolation(
                    key='-',
                    parent='-',
                    field=field)
            self._violations.append(violation)
