from typing import Union
from collections import namedtuple

Rule = namedtuple("Rule", ["name", "rtype", "is_required"])

# The support types that can be present in the YAML file
Data = Union[dict, list, int, float, str]


class RuleType:
    def __init__(self, type: Union[str, type], lookup: str = None, sub_type=None):
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
