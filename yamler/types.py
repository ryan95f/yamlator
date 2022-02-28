from abc import ABC
from enum import Enum
from typing import Iterator, Union
from collections import namedtuple

Rule = namedtuple("Rule", ["name", "rtype", "is_required"])
EnumItem = namedtuple("EnumItem", ["name", "value"])

# The support types that can be present in the YAML file
Data = Union[dict, list, int, float, str]


class RuleType:
    def __init__(self, type: Union[str, type], lookup: str = None,
                 sub_type: 'RuleType' = None):
        """RuleType constructor

        Args:
            type        (str | type): The expected type for a field. Use the str for
            a `ruleset` and other types will use the build in Python types

            lookup      (str):        Used when type=`ruleset`, this specifies the
            ruleset to lookup when processing the YAML file

            sub_type    (RuleType): A nested subtype for the type. Used when there are
            nested list types e.g list(list(int))
        """
        self.type = type
        self.lookup = lookup
        self.sub_type = sub_type

    def __repr__(self) -> str:
        if self.type == "ruleset":
            repr_template = "{}(type=ruleset, lookup={}, sub_type={})"
            return repr_template.format(self.__class__.__name__,
                                        self.lookup,
                                        self.sub_type)

        repr_template = "{}(type={}, sub_type={})"
        return repr_template.format(self.__class__.__name__,
                                    self.type.__name__,
                                    self.sub_type)


class ContainerTypes(Enum):
    RULESET = 0
    ENUM = 1


class YamlerType:
    def __init__(self, name: str, type: ContainerTypes):
        self.name = name
        self.type = type


class YamlerRuleSet(YamlerType):
    def __init__(self, name: str, rules: dict):
        super().__init__(name, ContainerTypes.RULESET)
        self.rules = rules


class YamlerEnum(YamlerType):
    def __init__(self, name: str, items: dict):
        super().__init__(name, ContainerTypes.ENUM)
        self.items = items
