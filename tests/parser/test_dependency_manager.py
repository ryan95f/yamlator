import unittest

from yamlator.parser.dependency import DependencyManager


class TestDependencyManager(unittest.TestCase):
    def test_dependency_without_cycle(self):
        mgmr = DependencyManager()
        n1 = mgmr.add('n1')
        n2 = mgmr.add('n2')
        n3 = mgmr.add('n3')
        mgmr.add('n4')

        mgmr.add_child(n1, 'n2')
        mgmr.add_child(n1, 'n3')

        mgmr.add_child(n2, 'n3')
        mgmr.add_child(n3, 'n4')

        has_cycyle = mgmr.hash_cycle(n1)
        self.assertFalse(has_cycyle)

    def test_dependency_with_cycle(self):
        mgmr = DependencyManager()
        n1 = mgmr.add('n1')
        n2 = mgmr.add('n2')
        mgmr.add('n3')

        mgmr.add_child(n1, 'n2')
        mgmr.add_child(n1, 'n3')

        mgmr.add_child(n2, 'n1')

        has_cycyle = mgmr.hash_cycle(n1)
        self.assertTrue(has_cycyle)


if __name__ == '__main__':
    unittest.main()
