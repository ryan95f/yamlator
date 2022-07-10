"""Validator for handling regex data types"""


from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.violations import RegexTypeViolation
from .base_validator import Validator


class RegexValidator(Validator):
    """Validator to handle the regex type in a schema"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate a regex rule type against a string. If the data
        is not a string type, then a `TypeViolation` is added to
        the violation list. If the string does not match the regex
        rule, then a `RegexTypeViolation` is added to the violation list

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        is_regex_type = (rtype.schema_type == SchemaTypes.REGEX)
        if not is_regex_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        if not isinstance(data, str):
            message = f'{key} should be of type str'
            self._add_type_violation(key, parent, message)
            return

        if not rtype.regex.search(data):
            violation = RegexTypeViolation(key, parent, data, rtype.regex)
            self._violations.append(violation)
            return
