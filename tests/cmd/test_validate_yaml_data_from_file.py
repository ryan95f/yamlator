"""Test cases for the validate_yaml_data_from_file function

Test Cases:
    * `test_validate_yaml_data_from_file_with_invalid_args` tests that the
      expected exception is raised when invalid arguments are provided
    * `test_validate_yaml_data_from_file_with_valid_data` with expected
       valid data provides the correct amount of violations
"""


import unittest

from typing import Type
from collections import namedtuple
from parameterized import parameterized

from yamlator.cmd import validate_yaml_data_from_file
from yamlator.exceptions import InvalidSchemaFilenameError

from tests.cmd import constants


EMPTY_STR = ''
VALID_YAML_DATA_FILE_PATH = './tests/files/valid/valid.yaml'
VALID_SCHEMA_FILE_PATH = './tests/files/valid/valid.ys'

ValidateArgs = namedtuple('ValidateArgs', ['yaml_filepath', 'schema_filepath'])


class TestValidateYamlDataFromFile(unittest.TestCase):
    """Test the `validate_yaml_data_from_file` function with
    valid and invalid arguments that would be expected as input
    when the CLI is used
    """

    @parameterized.expand([
        ('none_yaml_path',
            ValidateArgs(None, constants.VALID_SCHEMA), ValueError),
        ('none_schema_path',
            ValidateArgs(constants.VALID_YAML_DATA, None), ValueError),
        ('none_yaml_and_schema_path',
            ValidateArgs(None, None), ValueError),
        ('empty_yaml_path_str', ValidateArgs(
            EMPTY_STR, constants.VALID_SCHEMA
        ), ValueError),
        ('empty_schema_path_str', ValidateArgs(
            constants.VALID_YAML_DATA,
            EMPTY_STR
        ), ValueError),
        ('empty_yaml_and_path_str', ValidateArgs(
            EMPTY_STR,
            EMPTY_STR
        ), ValueError),
        ('yaml_data_file_not_found', ValidateArgs(
            'not_found.yaml',
            constants.VALID_SCHEMA
        ), FileNotFoundError),
        ('schema_file_not_found', ValidateArgs(
            constants.VALID_YAML_DATA,
            'not_found.ys'
        ), FileNotFoundError),
        ('schema_invalid_file_extension', ValidateArgs(
            constants.VALID_YAML_DATA,
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
        expected_violation_count = 0
        violations = validate_yaml_data_from_file(
            yaml_filepath=VALID_YAML_DATA_FILE_PATH,
            schema_filepath=VALID_SCHEMA_FILE_PATH
        )
        actual_violation_count = len(violations)

        self.assertIsNotNone(violations)
        self.assertEqual(expected_violation_count,
                         actual_violation_count)


if __name__ == '__main__':
    unittest.main()
