"""This module maintains all the types that are used by Yamlator"""

import re
import enum

from typing import Union
from typing import Iterator
from collections import namedtuple

Rule = namedtuple('Rule', ['name', 'rtype', 'is_required'])
EnumItem = namedtuple('EnumItem', ['name', 'value'])

# The support types that can be present in the YAML file
Data = Union[dict, list, int, float, str]


class SchemaTypes(enum.Enum):
    """Represents the support types that can be defined in a schema"""

    STR = enum.auto()
    INT = enum.auto()
    FLOAT = enum.auto()
    MAP = enum.auto()
    LIST = enum.auto()
    ENUM = enum.auto()
    RULESET = enum.auto()
    ANY = enum.auto()
    REGEX = enum.auto()
    BOOL = enum.auto()
    UNION = enum.auto()


class RuleType:
    """Represents a rule's data type that is defined in the Yamlator schema

    For example, given the following rules:

    ```text
        foo str required
        bar list(str) optional
    ```

    The types `str` and `list(str)` will be represented as RuleTypes

    Attributes:
        schema_type (yamlator.types.SchemaTypes): The type that this rule
            is representing. E.g int, list, ruleset, etc

        lookup (str): The lookup value that is used to fetch the relevant
            container type. This is only used by Enums or Rulesets. For other
            types this will be `None`

        sub_type (yamlator.types.RuleType): The sub type when a rule it using
            a list or a map data type. For example, given the type list(str),
            the sub type will be a `RuleType` for the string. For other types
            this will be `None`

        regex (str): The regular expression string used when the rule type is
            `SchemaTypes.REGEX`. For other types this will be `None`
    """

    def __init__(self, schema_type: SchemaTypes, lookup: str = None,
                 sub_type: 'RuleType' = None, regex: str = None) -> None:
        """RuleType init

        Args:
            schema_type (yamlator.types.SchemaTypes): The field type

            lookup (str, optional): Used when `schema_type` is
                `SchemaTypes.RULESET` or `SchemaTypes.ENUM`. This
                specifies the custom type to lookup when validating
                the data structure

            sub_type (yamlator.types.RuleType, optional): The sub type used
                when the `schema_type` is `SchemaTypes.MAP` or
                `SchemaTypes.LIST`. For example, given `list(str)`, the
                sub type will be a rule type representing the string

            regex (str, optional): The regex string that is used
                when `schema_type` is `SchemaTypes.REGEX`
        """
        self._regex = None
        self._schema_type = schema_type
        self._lookup = lookup
        self._sub_type = sub_type
        self._raw_regex = regex

        if regex is not None:
            self._regex = re.compile(regex)

    @property
    def schema_type(self):
        return self._schema_type

    @property
    def lookup(self) -> str:
        return self._lookup

    @property
    def sub_type(self) -> 'RuleType':
        return self._sub_type

    @property
    def regex(self):
        return self._regex

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
    """Represents a Union data type that is defined in the Yamlator schema

    Attributes:
        sub_types (Iterator[yamlator.types.RuleType]): A list of sub types
            that are considered valid types when validating the data. For
            example, given `Union(int, str)`, a rule type will be created
            for the `int` and `str`
    """

    def __init__(self, sub_types: 'Iterator[RuleType]') -> None:
        """UnionRuleType init

        Args:
            sub_types (Iterator[yamlator.types.RuleType]): An iterable of rule
                types that the union will compare
        """
        super().__init__(SchemaTypes.UNION)
        self._sub_types = sub_types

    @property
    def sub_types(self) -> 'Iterator[RuleType]':
        return self._sub_types

    def __str__(self) -> str:
        sub_types_strings = [None] * len(self.sub_types)
        for idx, sub_type in enumerate(self.sub_types):
            sub_types_strings[idx] = str(sub_type)
        combined_sub_types_strings = ', '.join(sub_types_strings)
        return f'union({combined_sub_types_strings})'


class ContainerTypes(enum.Enum):
    """Enum of custom types used by Yamlator"""
    RULESET = 0
    ENUM = 1


class YamlatorType:
    """Base class for custom Yamlator types. Commonly used to represent
    container types such as Rulesets and Enums

    Attributes:
        name (str): The name of the type as defined in the schema.
            For example, given the following: `ruleset Foo {}`,
            then the name used in this class will be `Foo`

        container_type (yamlator.types.ContainerTypes): Enum
            representation of the current type
    """

    def __init__(self, name: str, container_type: ContainerTypes):
        """YamlatorType init

        Args:
            name            (str): The object name of the type
            container_type  (yamlator.types.ContainerTypes): The type of
                object being represented
        """
        self._name = name
        self._container_type = container_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def container_type(self) -> ContainerTypes:
        return self._container_type

    def __repr__(self) -> str:
        return f'{self.container_type}({self.name})'


class YamlatorRuleset(YamlatorType):
    """Represent a Ruleset type. A ruleset will contain a list of
    rules that the data is validated against

    Attributes:
        name (str): The name of the type as defined in the schema.
            For example, given the following: `ruleset Foo {}`,
            then the name used in this class will be `Foo`

        container_type (yamlator.types.ContainerTypes): Enum
            representation of the current type. This will always be
            `ContainerTypes.RULESET`

        rules (Iterator[yamlator.types.Rule]): The list of rules in the ruleset

        is_strict (bool, optional): If the ruleset is in strict mode. When
            enabled any additional keys that are not part of the ruleset
            will raise a strict mode violation
    """

    def __init__(self, name: str, rules: Iterator[Rule],
                 is_strict: bool = False):
        """YamlatorRuleset init

        Args:
            name (str): The name of the ruleset
            rules (list): A list of rules for the ruleset
            is_strict (bool, optional): Sets the ruleset to be in strict mode.
                When used with the validators, it will check to ensure any
                extra fields are raised as a violation
        """
        super().__init__(name, ContainerTypes.RULESET)
        self._rules = rules
        self._is_strict = is_strict

    @property
    def rules(self) -> Iterator[Rule]:
        return self._rules

    @property
    def is_strict(self) -> bool:
        return self._is_strict


class YamlatorEnum(YamlatorType):
    """Represents a Yamlator Enum Type

    Attributes:
        name (str): The name of the type as defined in the schema. For example,
            given the following: `enum Foo {}`, then the name used in this
            class will be `Foo`

        container_type (yamlator.types.ContainerTypes): Enum representation
            of the current type. This will always be `ContainerTypes.ENUM`

        items (dict): The individual enum items stored as a key value pair.
            See example below.

    Example:
        The dict of items will be in the format:
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
            name (str): The name of the enum
            items (dict): A dict containing a lookup of the expected values
                in the enum
        """
        super().__init__(name, ContainerTypes.ENUM)
        self._items = items

    @property
    def items(self) -> dict:
        return self._items.copy()
