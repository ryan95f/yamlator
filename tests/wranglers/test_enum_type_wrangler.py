import unittest

from yamler.types import EnumItem, RuleType, YamlerEnum

from .base import BaseWranglerTest
from parameterized import parameterized
from yamler.wranglers import EnumTypeWrangler


class TestEnumTypeWrangler(BaseWranglerTest):
    def setUp(self):
        super().setUp()
        self.enums = {
            'message': YamlerEnum("message", {
                "success": EnumItem('VALID', "success"),
                "failure": EnumItem('INVALID', "failure")
            })
        }

    @parameterized.expand([
        ('with_valid_enum_value', "success", RuleType(type="enum", lookup='message'), 0),
        ('with_invalid_enum_value', "not_found",
            RuleType(type="enum", lookup='message'), 1),
        ('with_str_rule_type', "success", RuleType(type=str), 0),
        ('with_enum_not_found', "success", RuleType(type="enum", lookup='errors'), 1)
    ])
    def test_enum_wrangler(self, name, data: str, rtype: RuleType,
                           expected_violation_count: int):
        wrangler = EnumTypeWrangler(self.violation_manager, self.enums)
        wrangler.wrangle(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        violation_count = len(self.violation_manager.violations)
        self.assertEqual(expected_violation_count, violation_count)

if __name__ == '__main__':
    unittest.main()
