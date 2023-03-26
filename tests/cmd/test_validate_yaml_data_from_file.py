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


ValidateArgs = namedtuple('ValidateArgs', ['yaml_filepath', 'schema_filepath'])


class TestValidateYamlDataFromFile(unittest.TestCase):
    """Test the `validate_yaml_data_from_file` function with
    valid and invalid arguments that would be expected as input
    when the CLI is used
    """

    @parameterized.expand([
        ('none_yaml_path', ValidateArgs(
            constants.NONE_PATH,
            constants.VALID_SCHEMA
        ), ValueError),
        ('none_schema_path', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.NONE_PATH
        ), ValueError),
        ('none_yaml_and_schema_path', ValidateArgs(
            constants.NONE_PATH,
            constants.NONE_PATH
        ), ValueError),
        ('empty_yaml_path_str', ValidateArgs(
            constants.EMPTY_PATH,
            constants.VALID_SCHEMA
        ), ValueError),
        ('empty_schema_path_str', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.EMPTY_PATH
        ), ValueError),
        ('empty_yaml_and_path_str', ValidateArgs(
             constants.EMPTY_PATH,
             constants.EMPTY_PATH
        ), ValueError),
        ('yaml_data_file_not_found', ValidateArgs(
            constants.NOT_FOUND_YAML_DATA,
            constants.VALID_SCHEMA
        ), FileNotFoundError),
        ('schema_file_not_found', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.NOT_FOUND_SCHEMA
        ), FileNotFoundError),
        ('schema_invalid_file_extension', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.INVALID_SCHEMA_EXTENSION
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
            yaml_filepath=constants.VALID_YAML_DATA,
            schema_filepath=constants.VALID_SCHEMA
        )
        actual_violation_count = len(violations)

        self.assertIsNotNone(violations)
        self.assertEqual(expected_violation_count,
                         actual_violation_count)


if __name__ == '__main__':
    unittest.main()
