"""Validator for handling the any data type"""


from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators.base_validator import Validator


class UnionTypeValidator(Validator):
    """Validator to handle the `union` type. This type accepts multiple types
    and will consider any one of them passing as valid"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate any rules that have the data marked as the `union` type

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        is_union_type = (rtype.schema_type == SchemaTypes.UNION)
        if not is_union_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        return
