"""Validator for handling lists types"""


from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators.base_validator import Validator


class ListValidator(Validator):
    """Validator for handling list types"""

    _ruleset_validator: Validator = None

    def set_ruleset_validator(self, validator: Validator) -> None:
        """Set a validator for handling nested rulesets in the list

        Args:
            validator (Validator): The validator to handle rulesets
        """
        self._ruleset_validator = validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the list data. This validator will recursive if
        nested lists are detected in the rule

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        is_list_data = isinstance(data, list)
        is_list_rule = (rtype.schema_type == SchemaTypes.LIST)

        if not is_list_rule:
            super().validate(key, data, parent, rtype, is_required)
            return

        if not is_list_data:
            message = f'{key} should be of type list'
            self._add_type_violation(key, parent, message)
            return

        for idx, item in enumerate(data):
            current_key = f'{key}[{idx}]'

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

    def _run_ruleset_validator(self, key: str, parent: str, data: Data,
                               rtype: RuleType) -> None:
        has_ruleset_validator = (self._ruleset_validator is not None)
        is_ruleset_rule = (rtype.schema_type == SchemaTypes.RULESET)

        if has_ruleset_validator and is_ruleset_rule:
            self._ruleset_validator.validate(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )
