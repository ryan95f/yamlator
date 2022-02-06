from typing import Union
from collections import namedtuple

Rule = namedtuple("Rule", ["name", "rtype", "is_required"])

# The support types that can be present in the YAML file
Data = Union[dict, list, int, float, str]
