"""Test cases for the `validate_yaml_data_from_file` function

Test Cases:
    * `test_validate_yaml_data_from_file_with_invalid_args` tests the validation
       process with a range of invalid arguments that a user could enter
       via the CLI
    * `test_validate_yaml_data_from_file_with_valid_data` with expected
       valid data
"""


import unittest

from typing import Type
from collections import namedtuple
from parameterized import parameterized

from yamlator.cmd import validate_yaml_data_from_file
from yamlator.exceptions import InvalidSchemaFilenameError

EMPTY_STR = ''
VALID_YAML_DATA_FILE_PATH = './tests/files/example/example.yaml'
VALID_SCHEMA_FILE_PATH = './tests/files/example/example.ys'

ValidateArgs = namedtuple('ValidateArgs', ['yaml_filepath', 'schema_filepath'])


class TestValidateYamlDataFromFile(unittest.TestCase):
    """Test the `validate_yaml_data_from_file` function with
    valid and invalid arguments that would be expected as input
    when the CLI is used
    """

    @parameterized.expand([
        ('none_yaml_path',
            ValidateArgs(None, VALID_SCHEMA_FILE_PATH), ValueError),
        ('none_schema_path',
            ValidateArgs(VALID_YAML_DATA_FILE_PATH, None), ValueError),
        ('none_yaml_and_schema_path',
            ValidateArgs(None, None), ValueError),
        ('empty_yaml_path_str', ValidateArgs(
            EMPTY_STR, VALID_SCHEMA_FILE_PATH
        ), ValueError),
        ('empty_schema_path_str', ValidateArgs(
            VALID_YAML_DATA_FILE_PATH,
            EMPTY_STR
        ), ValueError),
        ('empty_yaml_and_path_str', ValidateArgs(
            EMPTY_STR,
            EMPTY_STR
        ), ValueError),
        ('yaml_data_file_not_found', ValidateArgs(
            'not_found.yaml',
            VALID_SCHEMA_FILE_PATH
        ), FileNotFoundError),
        ('schema_file_not_found', ValidateArgs(
            VALID_YAML_DATA_FILE_PATH,
            'not_found.ys'
        ), FileNotFoundError),
        ('schema_invalid_file_extension', ValidateArgs(
            VALID_YAML_DATA_FILE_PATH,
            './tests/files/hello.ruleset'
        ), InvalidSchemaFilenameError)
    ])
    def test_validate_yaml_data_from_file_with_invalid_args(self, name: str,
                                                            args: ValidateArgs,
                                                            expected_exception: Type[Exception]):  # nopep8 pylint: disable=C0301
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            validate_yaml_data_from_file(args.yaml_filepath,
                                         args.schema_filepath)

    def test_validate_yaml_data_from_file_with_valid_data(self):
        violations = validate_yaml_data_from_file(
            yaml_filepath=VALID_YAML_DATA_FILE_PATH,
            schema_filepath=VALID_SCHEMA_FILE_PATH
        )
        self.assertIsNotNone(violations)


if __name__ == '__main__':
    unittest.main()
