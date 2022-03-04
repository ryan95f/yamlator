import unittest

from collections import namedtuple
from yamler.parser import YamlerTransformer
from yamler.types import EnumItem


Token = namedtuple('Token', ['value'])


class TestYamlerTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = YamlerTransformer()

    def test_enum(self):
        enum_items = [
            EnumItem("SUCCESS", "success"),
            EnumItem("ERR", "error")
        ]
        tokens = (Token('StatusCode'), *enum_items)
        enum = self.transformer.enum(tokens)
        self.assertIsNotNone(enum)
        self.assertEqual('StatusCode', enum.name)
        self.assertEqual(len(enum_items), len(enum.items))


if __name__ == '__main__':
    unittest.main()
