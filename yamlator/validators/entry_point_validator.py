"""Validator for handling the entry point ruleset"""


from collections import deque
from typing import Iterable

from yamlator.types import Data
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import YamlatorRuleset
from yamlator.violations import StrictEntryPointViolation
from yamlator.utils import is_keyless_rule
from .base_validator import Validator


class EntryPointValidator(Validator):
    """Validator to handle the `schema` / entry point of the Yamlator rules"""

    def __init__(self, violations: deque, entry_point: YamlatorRuleset):
        """EntryPointValidator init

        Args:
            violations (collections.deque): Contains violations that have been
                detected whilst processing the data

            entry_point (yamlator.types.YamlatorRuleset): The entry
                point ruleset
        """
        self._entry_point = entry_point
        self._flat_validator = None
        super().__init__(violations)

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the entry point ruleset and validate each
        rule by calling the next validator in the chain

        Args:
            key (str): The data field name
            data (yamlator.types.Data): The data to validate
            parent (str): The parent key of the data
            rtype (yamlator.types.RuleType): The type assigned to the
                rule that will be applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        # These are not used by the `EntryPointValidator`
        del key
        del rtype
        del is_required

        rules = self._entry_point.rules
        if not rules:
            return

        has_validated = self._validate_keyless_data(data, parent, rules)
        if has_validated:
            return

        if self._entry_point.is_strict:
            self._handle_strict_mode(data, rules)

        for rule in rules:
            sub_data = data.get(rule.name, None)

            super().validate(rule.name, sub_data, parent,
                             rule.rtype, rule.is_required)

    def _validate_keyless_data(self, data: Data,
                               parent: str,
                               rules: Iterable[Rule]):
        # If there is more than 1 rule, that we are not
        # dealing with a keyless root
        if len(rules) > 1:
            return False

        rule: Rule = rules[0]
        if not is_keyless_rule(rule):
            return False

        # Run the validation here instead since we are dealing
        # with an object that does not have a root key. E.g a list
        super().validate(rule.name, data, parent,
                         rule.rtype, rule.is_required)
        return True

    def _handle_strict_mode(self, data: dict, rules: Iterable[Rule]):
        rule_fields = {rule.name for rule in rules}
        data_fields = set(data.keys())
        extra_fields = data_fields - rule_fields

        for field in extra_fields:
            violation = StrictEntryPointViolation(
                    key='SCHEMA',
                    parent='-',
                    field=field)
            self._violations.append(violation)
