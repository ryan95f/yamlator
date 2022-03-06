import unittest

from yamler.types import RuleType, SchemaTypes
from yamler.violations import ViolationManager


class BaseWranglerTest(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(type=SchemaTypes.STR)
        self.violation_manager = ViolationManager()
