from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from .base_validator import Validator


class MapValidator(Validator):
    """Validator to handle map types"""

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data contained within in a map

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        is_map_rule = (rtype.type == SchemaTypes.MAP)
        is_map_data = isinstance(data, dict)

        if not is_map_rule:
            super().validate(key, data, parent, rtype, is_required)
            return

        if not is_map_data:
            self._add_type_violation(key, parent, f'{key} should be of type map')
            return

        for child_key, value in data.items():
            self.validate(
                key=child_key,
                data=value,
                parent=key,
                rtype=rtype.sub_type)
