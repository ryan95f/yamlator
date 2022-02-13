import unittest
from unittest.mock import patch
from yamler.types import Rule, RuleType

from yamler.wranglers import OptionalWrangler
from yamler.violations import ViolationManager


class TestOptionalWrangler(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.data = 'hello world'
        self.rtype = RuleType(type=str)
        self.required = False

        self.violation_manager = ViolationManager
        self.wrangler = OptionalWrangler(self.violation_manager)

    def test_wrangler_with_optional_data(self):
        self.wrangler.wrangle(
            key=self.key,
            data=self.data,
            parent=self.parent,
            rtype=self.rtype,
            is_required=self.required)


if __name__ == '__main__':
    unittest.main()
