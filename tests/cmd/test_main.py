"""Test the main (entry point) of the command line

Test Cases:
    * `test_main` tests the entry point with different arguments
       to validate the correct status code is provided
"""


import io
import unittest

from collections import namedtuple
from parameterized import parameterized
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from yamlator.cmd import main
from yamlator.cmd import DisplayMethod
from yamlator.cmd.outputs import SuccessCode

from tests.cmd import constants


ValidateArgs = namedtuple('ValidateArgs', ['file', 'ruleset_schema', 'output'])


class TestMain(unittest.TestCase):
    """Test cases for the `main` method of the command line"""

    @parameterized.expand([
        ('with_yaml_matching_ruleset', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.VALID_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.SUCCESS),
        ('with_yaml_containing_ruleset_violations', ValidateArgs(
            constants.INVALID_YAML_DATA,
            constants.VALID_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_ruleset_file_not_found', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.NOT_FOUND_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_yaml_data_not_found', ValidateArgs(
            constants.NOT_FOUND_YAML_DATA,
            constants.VALID_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_empty_yaml_file_path', ValidateArgs(
            constants.EMPTY_PATH,
            constants.VALID_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_empty_ruleset_path', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.EMPTY_PATH,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_invalid_ruleset_extension', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.INVALID_SCHEMA_EXTENSION,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_syntax_errors', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.INVALID_ENUM_NAME_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_ruleset_not_defined', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.MISSING_RULESET_DEF_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR),
        ('with_cyle_in_ruleset', ValidateArgs(
            constants.VALID_YAML_DATA,
            constants.SELF_CYCLE_SCHEMA,
            DisplayMethod.TABLE.value
        ), SuccessCode.ERR)
    ])
    @patch('argparse.ArgumentParser')
    def test_main(self, name: str, args: ValidateArgs,
                  expected_status_code: int, mock_args_parser: Mock):
        # Unused by test case, however is required by the parameterized library
        del name

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = args
        mock_args_parser.return_value = mock_parser

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = main()
            self.assertEqual(expected_status_code, status_code)


if __name__ == '__main__':
    unittest.main()
