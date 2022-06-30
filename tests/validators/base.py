"""Contains the base test case class for testing any of the validators"""

import unittest

from collections import deque
from yamlator.types import RuleType
from yamlator.types import SchemaTypes


class BaseValidatorTest(unittest.TestCase):
    """Base test case for testing any validators"""

    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(schema_type=SchemaTypes.STR)
        self.violations = deque()
