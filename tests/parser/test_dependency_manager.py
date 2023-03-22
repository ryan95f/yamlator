import unittest

from yamlator.parser.dependency import DependencyManager


class TestDependencyManager(unittest.TestCase):
    def test_dependency_without_cycle(self):
        mgmr = DependencyManager()
        n1 = mgmr.add('n1')
        n2 = mgmr.add('n2')
        n3 = mgmr.add('n3')
        n4 = mgmr.add('n4')

        mgmr.add_child(n1, n2)
        mgmr.add_child(n1, n3)

        mgmr.add_child(n2, n3)
        mgmr.add_child(n3,  n4)

        has_cycyle = mgmr.has_cycle()
        self.assertFalse(has_cycyle)

    def test_dependency_with_cycle(self):
        mgmr = DependencyManager()
        n1 = mgmr.add('n1')
        n2 = mgmr.add('n2')
        n3 = mgmr.add('n3')

        mgmr.add_child(n1, n2)
        mgmr.add_child(n1, n3)

        mgmr.add_child(n2, n1)

        has_cycyle = mgmr.has_cycle()
        self.assertTrue(has_cycyle)

    def test_dependency_node_self_cycle(self):
        mgmr = DependencyManager()
        n1 = mgmr.add('n1')
        mgmr.add_child(n1, n1)

        has_cycle = mgmr.has_cycle()
        self.assertTrue(has_cycle)

    def test_add(self):
        mgmr = DependencyManager()
        n1_v1 = mgmr.add('n1')
        n1_v2 = mgmr.add('n1')
        self.assertEqual(n1_v1, n1_v2)


if __name__ == '__main__':
    unittest.main()
