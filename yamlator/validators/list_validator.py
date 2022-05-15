from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from .base_validator import Validator


class ListValidator(Validator):
    """Validtor for handling list types"""

    ruleset_validator: Validator = None

    def set_ruleset_validator(self, validator: Validator) -> None:
        """Set a validator for when nested rulesets are within the list

        Args:
            validator (Validator): The validator to handle rulesets
        """
        self.ruleset_validator = validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the list data. This validator will recursive if
        nested lists are detected in the rule

        Args:
            key              (str): The key to the data
            data            (Data): The data to validate
            parent           (str): The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required     (bool): Is the rule required
        """
        is_list_data = isinstance(data, list)
        is_list_rule = (rtype.type == SchemaTypes.LIST)

        if not is_list_rule:
            super().validate(key, data, parent, rtype, is_required)
            return

        if not is_list_data:
            self._add_type_violation(key, parent, f'{key} should be of type list')
            return

        for idx, item in enumerate(data):
            current_key = f"{key}[{idx}]"

            # loop over any nested lists
            self.validate(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

            # a list could contain ruleset items
            # so need to run each item through that validator
            self._run_ruleset_validator(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

    def _run_ruleset_validator(self, key: str, parent: str, data: Data, rtype: RuleType):
        has_ruleset_validator = (self.ruleset_validator is not None)
        is_ruleset_rule = (rtype.type == SchemaTypes.RULESET)

        if has_ruleset_validator and is_ruleset_rule:
            self.ruleset_validator.validate(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )
