import unittest

from collections import namedtuple
from parameterized import parameterized
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorRuleset
from yamlator.parser.loaders import map_imported_resource


Params = namedtuple('Params', [
    'namespace',
    'resource_type',
    'resource_lookup',
    'imported_resources']
)


def create_hello_ruleset():
    return YamlatorRuleset('Hello', [
        Rule('msg', RuleType(SchemaTypes.STR), False)
    ])


NAMESPACE = 'test'
FAKE_RESOURCE_NAME = 'Fake'
HELLO_RESOURCE_NAME = 'Hello'
HELLO_RULESET = {
    'Hello': create_hello_ruleset()
}


class TestMapImportedResource(unittest.TestCase):
    @parameterized.expand([
        ('all_none_params', Params(None, None, None, None), ValueError),
        ('none_resource_type',
            Params(None, None, {}, {'Hello': HELLO_RULESET}), ValueError),
        ('none_resource_lookup',
            Params(None, HELLO_RESOURCE_NAME, None,
                   {'Hello': HELLO_RULESET}), ValueError),
        ('none_imported_resources',
            Params(None, HELLO_RESOURCE_NAME, {}, None), ValueError),
        ('namespace_wrong_type',
            Params(1, HELLO_RESOURCE_NAME, {}, None), TypeError),
        ('resource_name_wrong_type',
            Params(NAMESPACE, [HELLO_RESOURCE_NAME], {}, None), TypeError),
        ('resource_lookup_wrong_type',
            Params(NAMESPACE, HELLO_RESOURCE_NAME, [], None), TypeError),
        ('imported_resources_wrong_type',
            Params(NAMESPACE, HELLO_RESOURCE_NAME, {}, []), TypeError),
    ])
    def test_map_imported_resource_invalid_args(self, name: str,
                                                params: Params,
                                                expected_exception: Exception):
        del name

        with self.assertRaises(expected_exception):
            map_imported_resource(
                params.namespace,
                params.resource_type,
                params.resource_lookup,
                params.imported_resources
            )

    @parameterized.expand([
        ('with_resource_that_exists_without_namespace',
            Params(None, HELLO_RESOURCE_NAME, {}, HELLO_RULESET), True),
        ('with_resource_that_exists_with_namespace',
            Params(NAMESPACE, HELLO_RESOURCE_NAME, {}, HELLO_RULESET), True),
        ('with_resource_that_does_not_exist_without_namespace',
            Params(None, FAKE_RESOURCE_NAME, {}, HELLO_RULESET), False),
        ('with_resource_that_does_not_exist_with_namespace',
            Params(NAMESPACE, FAKE_RESOURCE_NAME, {}, HELLO_RULESET), False),
    ])
    def test_map_imported_resource(self, name: str, params: Params,
                                   expected_result: bool):
        del name

        result = map_imported_resource(
            params.namespace,
            params.resource_type,
            params.resource_lookup,
            params.imported_resources
        )
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
