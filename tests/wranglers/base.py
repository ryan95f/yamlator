import unittest

from collections import deque
from yamler.types import RuleType, SchemaTypes


class BaseWranglerTest(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(type=SchemaTypes.STR)
        self.violations = deque()
