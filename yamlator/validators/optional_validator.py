from yamlator.types import Data
from yamlator.types import RuleType
from .base_validator import Validator


class OptionalValidator(Validator):
    """Validator for handling optional rules"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate a key is an optional.

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """

        missing_data = data is None
        if not is_required and missing_data:
            return

        super().validate(key, data, parent, rtype, is_required)
