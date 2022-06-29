"""Test the `main` (entry point) of the command line

Test Cases:
    * `test_main` tests the entry point with different arguments
       to validate the correct status code is provided
"""


import io
import unittest

from collections import namedtuple
from parameterized import parameterized
from unittest.mock import MagicMock, Mock, patch

from yamlator.cmd import ERR
from yamlator.cmd import SUCCESS
from yamlator.cmd import main
from yamlator.cmd import DisplayMethod

HELLO_YAML_FILE_PATH = './tests/files/example/example.yaml'
HELLO_RULESET_FILE_PATH = './tests/files/example/example.ys'
INVALID_HELLO_YAML_FILE_PATH = './tests/files/example/invalid_example.yaml'

ValidateArgs = namedtuple('ValidateArgs', ['file', 'ruleset_schema', 'output'])


class TestMain(unittest.TestCase):
    """Test cases for the `main` method of the command line"""

    @parameterized.expand([
        ('with_yaml_matching_ruleset', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            HELLO_RULESET_FILE_PATH,
            DisplayMethod.TABLE.value
        ), SUCCESS),
        ('with_yaml_containing_ruleset_violations', ValidateArgs(
            INVALID_HELLO_YAML_FILE_PATH,
            HELLO_RULESET_FILE_PATH,
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_ruleset_file_not_found', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            '/test/files/not_found.ys',
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_yaml_data_not_found', ValidateArgs(
            './tests/files/not_found.yaml',
            HELLO_RULESET_FILE_PATH,
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_empty_yaml_file_path', ValidateArgs(
            '',
            HELLO_RULESET_FILE_PATH,
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_empty_ruleset_path', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            '',
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_invalid_ruleset_extension', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            './tests/files/hello.ruleset',
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_syntax_errors', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            './tests/files/invalid_files/invalid_enum_name.ys',
            DisplayMethod.TABLE.value
        ), ERR),
        ('with_ruleset_not_defined', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            './tests/files/invalid_files/missing_defined_ruleset.ys',
            DisplayMethod.TABLE.value
        ), ERR)
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
