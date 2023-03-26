"""Test cases for the DependencyManager class"""

import unittest

from yamlator.parser.dependency import DependencyManager


class TestDependencyManager(unittest.TestCase):
    """Test cases for the DependencyManager"""

    def setUp(self):
        self.dependencies = DependencyManager()

    def test_dependency_mgmr_add_returns_hash(self):
        content = 'Hello world'
        md5_hash = self.dependencies.add(content)
        self.assertIsNotNone(md5_hash)

    def test_dependency_mgmr_add_child_returns_true(self):
        parent_hash = self.dependencies.add('parent')
        child_content = 'Hello World'

        result = self.dependencies.add_child(parent_hash, child_content)
        self.assertTrue(result)

    def test_dependency_mgmr_add_child_without_parent_add_returns_true(self):
        parent_hash = 'abcdefghijk1233456'
        child_content = 'Hello World'

        result = self.dependencies.add_child(parent_hash, child_content)
        self.assertTrue(result)

    def test_dependency_mgmr_has_cycle_returns_false(self):
        n1 = self.dependencies.add('n1')
        n2 = self.dependencies.add('n2')
        n3 = self.dependencies.add('n3')
        n4 = self.dependencies.add('n4')

        self.dependencies.add_child(n1, n2)
        self.dependencies.add_child(n1, n3)
        self.dependencies.add_child(n2, n3)
        self.dependencies.add_child(n3,  n4)

        has_cycyle = self.dependencies.has_cycle()
        self.assertFalse(has_cycyle)

    def test_dependency_mgmr_has_cycle_returns_true(self):
        n1 = self.dependencies.add('n1')
        n2 = self.dependencies.add('n2')
        n3 = self.dependencies.add('n3')

        self.dependencies.add_child(n1, n2)
        self.dependencies.add_child(n1, n3)
        self.dependencies.add_child(n2, n1)

        has_cycyle = self.dependencies.has_cycle()
        self.assertTrue(has_cycyle)

    def test_dependency_mgmr_has_cycle_self_cycle_returns_true(self):
        n1 = self.dependencies.add('n1')
        self.dependencies.add_child(n1, n1)

        has_cycle = self.dependencies.has_cycle()
        self.assertTrue(has_cycle)


if __name__ == '__main__':
    unittest.main()
