import unittest

from yamler.types import RuleType
from yamler.violations import ViolationManager


class BaseWranglerTest(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(type=str)
        self.violation_manager = ViolationManager()
