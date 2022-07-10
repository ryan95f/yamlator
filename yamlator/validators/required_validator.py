"""Validator for handling required rules"""


from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.violations import RequiredViolation
from .base_validator import Validator


class RequiredValidator(Validator):
    """Validator for handling required rules"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate a key is a required rule

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """

        missing_data = data is None
        if is_required and missing_data:
            violation = RequiredViolation(key, parent)
            self._violations.append(violation)
            return

        super().validate(key, data, parent, rtype, is_required)
