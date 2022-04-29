import unittest

from collections import deque
from src.types import RuleType
from src.types import SchemaTypes


class BaseValidatorTest(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(type=SchemaTypes.STR)
        self.violations = deque()
