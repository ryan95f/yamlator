import unittest

from collections import deque
from yamlator.types import RuleType
from yamlator.types import SchemaTypes


class BaseValidatorTest(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(schema_type=SchemaTypes.STR)
        self.violations = deque()
