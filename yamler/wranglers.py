from __future__ import annotations
from abc import ABC
from typing import Iterable
from collections import deque, namedtuple

from yamler.violations import RequiredViolation
from yamler.violations import RulesetTypeViolation
from yamler.violations import TypeViolation

from yamler.types import Data
from yamler.types import Rule
from yamler.types import RuleType
from yamler.types import YamlerRuleSet
from yamler.types import SchemaTypes


def wrangle_data(yaml_data: Data, instructions: dict) -> deque:
    """Traverse through the data to find any violations against the provided
    instructions.

    Args:
        yaml_data (dict | list | int | float | str): The yaml data to validate

        instructions                         (dict): The instructions containing
        enums and rulesets that will be validated

    Returns:
        A deque with the violations that were detected in the data.

    Raises:
        ValueError if the parameters `yaml_data` or `instructions` are `None`.
    """
    if yaml_data is None:
        raise ValueError('yaml_data should not be None')

    if instructions is None:
        raise ValueError('instructions should not be None')

    entry_parent = '-'
    violations = deque()
    entry_point: YamlerRuleSet = instructions.get('main', YamlerRuleSet('main', []))

    wranglers = _create_wrangler_chain(
        ruleset_lookups=instructions.get('rules', {}),
        enum_looksups=instructions.get('enums', {}),
        violations=violations
    )

    entry_point_rules: Iterable[Rule] = entry_point.rules
    for rule in entry_point_rules:
        sub_data = yaml_data.get(rule.name, None)

        wranglers.wrangle(
            key=rule.name,
            data=sub_data,
            parent=entry_parent,
            rtype=rule.rtype,
            is_required=rule.is_required
        )

    return violations


def _create_wrangler_chain(ruleset_lookups: dict,
                           enum_looksups: dict,
                           violations: deque) -> Wrangler:

    root = OptionalWrangler(violations)
    any_type_wrangler = AnyTypeWrangler(violations)
    required_wrangler = RequiredWrangler(violations)
    map_wrangler = MapWrangler(violations)
    ruleset_wrangler = RuleSetWrangler(violations, ruleset_lookups)
    list_wrangler = ListWrangler(violations)
    enum_wrangler = EnumTypeWrangler(violations, enum_looksups)
    type_wrangler = BuildInTypeWrangler(violations)

    root.set_next_wrangler(required_wrangler)
    required_wrangler.set_next_wrangler(map_wrangler)
    map_wrangler.set_next_wrangler(ruleset_wrangler)

    ruleset_wrangler.set_next_ruleset_wrangler(root)
    ruleset_wrangler.set_next_wrangler(list_wrangler)

    list_wrangler.set_ruleset_wrangler(ruleset_wrangler)
    list_wrangler.set_next_wrangler(enum_wrangler)

    enum_wrangler.set_next_wrangler(any_type_wrangler)
    any_type_wrangler.set_next_wrangler(type_wrangler)
    return root


class Wrangler(ABC):
    _next_wrangler = None

    def __init__(self, violations: deque) -> None:
        """Wrangler constructor

        Args:
            violations (deque): Contains violations that have been detected
            whilst processing the data
        """
        self._violations = violations

    def set_next_wrangler(self, wrangler: Wrangler) -> Wrangler:
        """Set the next wrangler in the chain

        Args:
            wrangler (Wrangler): The next wrangler in the chain

        Returns:
            The object that was provided in the `wrangler` parameter
        """
        self._next_wrangler = wrangler
        return wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):
        """Wrangler the data to detect violations

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        if self._next_wrangler is not None:
            self._next_wrangler.wrangle(
                key=key,
                data=data,
                parent=parent,
                rtype=rtype,
                is_required=is_required
            )


class OptionalWrangler(Wrangler):
    """Wrangler for handling optional rules"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data to find any optional rules. If an optional rule is
        found and is None, then the next stage in the chain is not called otherwise
        it will be called.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        missing_data = data is None
        if not is_required and missing_data:
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RequiredWrangler(Wrangler):
    """Wrangler for handling data that is required"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data for required fields. If a required value
        is None, then it is added to the violation manager.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        missing_data = data is None
        if is_required and missing_data:
            violation = RequiredViolation(key, parent)
            self._violations.append(violation)
            return

        super().wrangle(key, data, parent, rtype, is_required)


class RuleSetWrangler(Wrangler):
    """Wrangler for handling rulesets"""

    _ruleset_wrangler: Wrangler = None

    def __init__(self, violations: deque, instructions: dict):
        """RuleSetWrangler Constructor

        Args:
            violations (deque):  Contains violations that have been detected
            whilst processing the data

            instructions (dict): A dict containering references to
            other rulesets
        """
        self.instructions = instructions
        super().__init__(violations)

    def set_next_ruleset_wrangler(self, wrangler: Wrangler) -> None:
        """Set the next wrangler for handling nested rulesets in the data

        Args:
            wrangler (Wrangler): The wrangler to add to the chain
        """
        self._ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False):
        """Wrangle the data rulesets and call the chain on the data itself to validate it.
        If the current rule is not a ruleset then the next wrangler is called
        in the chain. If the data is not in a dict format then a type violation is added.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        if not self._is_ruleset_rule(rtype):
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if not self._is_ruleset(data):
            violation = RulesetTypeViolation(key, parent)
            self._violations.append(violation)
            return

        ruleset_rules = self._retrieve_next_ruleset(rtype.lookup)

        for ruleset_rule in ruleset_rules:
            sub_data = data.get(ruleset_rule.name, None)

            if self._ruleset_wrangler is not None:
                self._ruleset_wrangler.wrangle(
                    key=ruleset_rule.name,
                    data=sub_data,
                    parent=key,
                    rtype=ruleset_rule.rtype,
                    is_required=ruleset_rule.is_required
                )

    def _is_ruleset_rule(self, rtype: RuleType) -> bool:
        return rtype.type == SchemaTypes.RULESET

    def _is_ruleset(self, data: Data) -> bool:
        return type(data) == dict

    def _retrieve_next_ruleset(self, ruleset_name: str) -> Iterable[Rule]:
        default_missing_ruleset = YamlerRuleSet(ruleset_name, [])
        ruleset = self.instructions.get(ruleset_name, default_missing_ruleset)
        return ruleset.rules


class ListWrangler(Wrangler):
    """Wrangler for handling list types"""

    ruleset_wrangler: Wrangler = None

    def set_ruleset_wrangler(self, wrangler: Wrangler) -> None:
        """Set a wrangler for when nested rulesets are within the list

        Args:
            wrangler (Wrangler): The wrangler to handle rulesets
        """
        self.ruleset_wrangler = wrangler

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the list data. If there is nested lists then this method
        will be recursively called. Any rulesets that are within the list will
        be handled by an additional wrangler that can be set with `set_ruleset_wrangler`.
        Any data type that is not a list is sent to the next wrangler.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """
        if not self._is_list_rule(rtype) or type(data) != list:
            super().wrangle(key, data, parent, rtype, is_required)
            return

        for idx, item in enumerate(data):
            current_key = f"{key}[{idx}]"

            # loop over any nested lists
            self.wrangle(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

            # a list could contain ruleset items
            # so need to run each item through that wrangler
            self._run_ruleset_wrangler(
                key=current_key,
                parent=key,
                data=item,
                rtype=rtype.sub_type
            )

    def _is_list_rule(self, rtype: RuleType):
        return rtype.type == SchemaTypes.LIST

    def _run_ruleset_wrangler(self, key: str, parent: str, data: Data, rtype: RuleType):
        has_ruleset_wrangler = self.ruleset_wrangler is not None
        is_ruleset_rule = rtype.type == SchemaTypes.RULESET

        if has_ruleset_wrangler and is_ruleset_rule:
            self.ruleset_wrangler.wrangle(
                key=key,
                parent=parent,
                data=data,
                rtype=rtype
            )


_SchemaTypeDecoder = namedtuple("SchemaTypeDecoder", ["type", "friendly_name"])


class BuildInTypeWrangler(Wrangler):
    """Wrangler to handle the build in types. e.g `int`, `list` & `str`"""

    def __init__(self, violations: ViolationManager) -> None:
        super().__init__(violations)
        self._built_in_lookups = {
            SchemaTypes.INT: _SchemaTypeDecoder(int, "int"),
            SchemaTypes.STR: _SchemaTypeDecoder(str, "str"),
            SchemaTypes.LIST: _SchemaTypeDecoder(list, "list"),
            SchemaTypes.MAP: _SchemaTypeDecoder(dict, "map"),
        }

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle the data to validate its data type. If the data matches
        the rule, then it is passed onto the next stage in the chain otherwise
        a `TypeViolation` is added to the violation manager.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """
        buildin_type = self._built_in_lookups.get(rtype.type)
        if buildin_type is None:
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if type(data) != buildin_type.type:
            message = f'{key} should be of type {buildin_type.friendly_name}'
            violation = TypeViolation(key, parent, message)
            self._violations.append(violation)
            return

        super().wrangle(key, data, parent, rtype, is_required)

    def _is_ruleset_type(self, rtype: RuleType) -> bool:
        return rtype.type == SchemaTypes.RULESET


class MapWrangler(Wrangler):
    """Wrangler to handle map types"""

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle map data. If the rule type is not a map, then this is
        passed to the next item in the chain. If it is a map type, then each
        element is iterated over and the wrangler will call itself to iterate
        over any nested maps.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        if not self._is_map_rule(rtype) or not self._is_map_type(data):
            super().wrangle(key, data, parent, rtype, is_required)
            return

        for child_key, value in data.items():
            self.wrangle(
                key=child_key,
                data=value,
                parent=key,
                rtype=rtype.sub_type)

    def _is_map_rule(self, rtype: RuleType):
        return rtype.type == SchemaTypes.MAP

    def _is_map_type(self, data: Data):
        return type(data) == dict


class AnyTypeWrangler(Wrangler):
    """Wrangler to handle the `any` type, which ignores all type
    checks against the data
    """

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle data when the rule marks the key as any type. This effectively
        ignores all type checks against the key. Any other rule that has a type
        besides `any` is passed onto the next wrangler in the chain.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """

        if self._is_any_type(rtype):
            return

        super().wrangle(key, data, parent, rtype, is_required)

    def _is_any_type(self, rtype: RuleType):
        return rtype.type == SchemaTypes.ANY


class EnumTypeWrangler(Wrangler):
    """Wrangler to handle data that is contained in a enum as a constant"""

    def __init__(self, violations: ViolationManager, enums: dict):
        """EnumTypeWrangler constructor

        Args:
            violations (deque): Contains violations that have been detected
            whilst processing the data

            enums       (dict): A dict that contains references to enums
            referenced in the rulesets.
        """
        super().__init__(violations)
        self.enums = enums

    def wrangle(self, key: str, data: Data, parent: str, rtype: RuleType,
                is_required: bool = False) -> None:
        """Wrangle enum data in the YAML and validate that
        there is a matching value in the rule. If a match is
        not found then a `TypeViolation` is added to the violation
        mamager. If the rule type is not a enum, then pass to the next
        wrangler.

        Args:
            key         (str):      The key that owns the data
            data        (Data):     The data to wrangler
            parent      (str):      The parent key of the data
            rtype       (RuleType): The type assigned to the rule
            is_required (bool):     Is the rule required
        """
        if not self._is_enum_rule(rtype):
            super().wrangle(key, data, parent, rtype, is_required)
            return

        if not self._is_enum_str_data(data):
            self._add_enum_violation(key, parent, rtype.lookup)
            return

        if self._matches_enum_data(data, rtype.lookup):
            return

        self._add_enum_violation(key, parent, rtype.lookup)

    def _is_enum_rule(self, rtype: RuleType) -> bool:
        return rtype.type == SchemaTypes.ENUM

    def _is_enum_str_data(self, data: Data):
        return isinstance(data, str)

    def _matches_enum_data(self, data: Data, enum_name: str) -> bool:
        target_enum = self.enums.get(enum_name, None)

        if target_enum is None:
            return False

        enum_value = target_enum.items.get(data, None)
        return enum_value is not None

    def _add_enum_violation(self, key: str, parent: str, enum_name: str):
        message = f'{key} does not match any value in enum {enum_name}'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)
