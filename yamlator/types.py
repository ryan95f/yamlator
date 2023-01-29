"""Yamlator Types"""

import re

from enum import Enum
from enum import auto
from typing import Union
from typing import Iterator
from collections import namedtuple

Rule = namedtuple('Rule', ['name', 'rtype', 'is_required'])
EnumItem = namedtuple('EnumItem', ['name', 'value'])

# The support types that can be present in the YAML file
Data = Union[dict, list, int, float, str]


class SchemaTypes(Enum):
    """Represents the support types that can be defined in a schema"""
    STR = auto()
    INT = auto()
    FLOAT = auto()
    MAP = auto()
    LIST = auto()
    ENUM = auto()
    RULESET = auto()
    ANY = auto()
    REGEX = auto()
    BOOL = auto()
    UNION = auto()


class RuleType:
    """Represents a rule's data type that is defined in the Yamlator schema"""

    regex = None

    def __init__(self, schema_type: SchemaTypes, lookup: str = None,
                 sub_type: 'RuleType' = None, regex: str = None) -> None:
        """RuleType init

        Args:
            schema_type        (SchemaTypes): The expected type for a field

            lookup              (str): Used when type=`ruleset` or type=`enum`.
            This specifies the custom type to lookup when processing the data

            sub_type       (RuleType): A nested subtype for the type.
            Used when there are nested list types e.g list(list(int))

            regex               (str): The regex string that is used
            when type=`regex`
        """
        self.schema_type = schema_type
        self.lookup = lookup
        self.sub_type = sub_type
        self._raw_regex = regex

        if regex is not None:
            self.regex = re.compile(regex)

    def __str__(self) -> str:
        types = {
            SchemaTypes.REGEX: f'Regex({self._raw_regex})',
            SchemaTypes.RULESET: self.lookup,
            SchemaTypes.ENUM: self.lookup,
            SchemaTypes.INT: 'int',
            SchemaTypes.STR: 'str',
            SchemaTypes.FLOAT: 'float',
            SchemaTypes.LIST: 'list({})',
            SchemaTypes.MAP: 'map({})',
            SchemaTypes.BOOL: 'bool',
            SchemaTypes.ANY: 'any'
        }

        type_str = types[self.schema_type]
        sub_type = self.sub_type
        while sub_type is not None:
            sub_type_str = types[sub_type.schema_type]
            type_str = type_str.format(sub_type_str)
            sub_type = sub_type.sub_type
        return type_str

    def __repr__(self) -> str:
        if self.schema_type == SchemaTypes.RULESET:
            repr_template = '{}(type=ruleset, lookup={}, sub_type={})'
            return repr_template.format(self.__class__.__name__,
                                        self.lookup,
                                        self.sub_type)

        repr_template = '{}(type={}, sub_type={})'
        return repr_template.format(self.__class__.__name__,
                                    self.schema_type,
                                    self.sub_type)


class UnionRuleType(RuleType):
    """Represents a Union data type that is defined in the Yamlator schema"""

    def __init__(self, sub_types: 'list[RuleType]') -> None:
        """UnionRuleType init

        Args:
            sub_types (list[RuleType]): A list of rule types that
            the union will compare
        """
        super().__init__(SchemaTypes.UNION)
        self.sub_types = sub_types

    def __str__(self) -> str:
        sub_types_strings = [None] * len(self.sub_types)
        for idx, sub_type in enumerate(self.sub_types):
            sub_types_strings[idx] = str(sub_type)
        combined_sub_types_strings = ', '.join(sub_types_strings)
        return f'union({combined_sub_types_strings})'


class ContainerTypes(Enum):
    """Enum of custom types that are used when defining a ruleset"""
    RULESET = 0
    ENUM = 1


class YamlatorType:
    """Base Class for custom types"""

    def __init__(self, name: str, container_type: ContainerTypes):
        """YamlatorType init

        Args:
            name            (str): The object name of the type
            container_type  (ContainerTypes): The type of object
            being represented
        """
        self.name = name
        self.container_type = container_type

    def __repr__(self) -> str:
        return f'{self.container_type}({self.name})'


class YamlatorRuleset(YamlatorType):
    """Represent a Ruleset Type. A ruleset will contain a list of
    rules of `RuleType` which will validated against
    """

    def __init__(self, name: str, rules: list, is_strict: bool = False):
        """YamlatorRuleset init

        Args:
            name       (str): The name of the ruleset
            rules     (list): A list of rules for the ruleset
            is_strict (bool): Sets the ruleset to be in strict mode.
            When used with the validators, it will check to ensure any
            extra fields are raised as a violation
        """
        super().__init__(name, ContainerTypes.RULESET)
        self._rules = rules
        self.is_strict = is_strict

    @property
    def rules(self) -> Iterator[Rule]:
        return self._rules


class YamlatorEnum(YamlatorType):
    """Represents a Enum Type that will contain a dict of valid
    values. The dict of items will be in the format:
    {
        <value>: EnumItem(<name>, <value>)
    }

    For example:
    {
        'success': EnumItem('SUCCESS', 'success'),
        'failure': EnumItem('FAILURE', 'failure'),
    }
    """

    def __init__(self, name: str, items: dict):
        """YamlatorEnum init

        Args:
            name     (str): The name of the enum
            items   (dict): A dict containing a lookup of
            the expected values in the enum
        """
        super().__init__(name, ContainerTypes.ENUM)
        self.items = items
