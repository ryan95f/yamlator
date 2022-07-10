"""Validator for handling rulesets types"""


from collections import deque
from typing import Iterable

from yamlator.types import Data
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorRuleset
from yamlator.violations import RulesetTypeViolation
from .base_validator import Validator


class RulesetValidator(Validator):
    """Validator for handling rulesets types"""

    _ruleset_validator: Validator = None

    def __init__(self, violations: deque, instructions: dict):
        """RulesetValidator init

        Args:
            violations (deque): contains violations that have been detected
                whilst processing the data
            instructions (dict): A dict containing references to other rulesets
        """
        self._instructions = instructions
        super().__init__(violations)

    def set_next_ruleset_validator(self, validator: Validator) -> None:
        """Set the next validator for handling nested rulesets

        Args:
            validator (Validator): The ruleset validator
        """
        self._ruleset_validator = validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False):
        """Validate the data against the ruleset type.

        For example, given the following ruleset:

        ```
        ruleset MyData {
            message str
            number int
        }
        ```

        Then if the ruleset is assigned as a type to a rule, then this validator
        will traverse the entire sub structure of the data to validate
        that all the above data keys and data types are present.

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """

        is_ruleset_rule = (rtype.schema_type == SchemaTypes.RULESET)
        if not is_ruleset_rule:
            super().validate(key, data, parent, rtype, is_required)
            return

        is_ruleset_data = isinstance(data, dict)
        if not is_ruleset_data:
            violation = RulesetTypeViolation(key, parent)
            self._violations.append(violation)
            return

        ruleset_rules = self._retrieve_next_ruleset(rtype.lookup)

        for ruleset_rule in ruleset_rules:
            sub_data = data.get(ruleset_rule.name, None)

            if self._ruleset_validator is not None:
                self._ruleset_validator.validate(
                    key=ruleset_rule.name,
                    data=sub_data,
                    parent=key,
                    rtype=ruleset_rule.rtype,
                    is_required=ruleset_rule.is_required
                )

    def _retrieve_next_ruleset(self, ruleset_name: str) -> Iterable[Rule]:
        default_missing_ruleset = YamlatorRuleset(ruleset_name, [])
        ruleset = self._instructions.get(ruleset_name, default_missing_ruleset)
        return ruleset.rules
