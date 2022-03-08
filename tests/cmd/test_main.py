import io
import unittest

from collections import namedtuple
from parameterized import parameterized
from unittest.mock import MagicMock, Mock, patch
from yamler.cmd import main, SUCCESS, ERR

HELLO_YAML_FILE_PATH = './tests/files/hello.yaml'
HELLO_RULESET_FILE_PATH = './tests/files/hello.yamler'
INVALID_HELLO_YAML_FILE_PATH = './test/files/invalid_hello.yaml'

ValidateArgs = namedtuple('ValidateArgs', ['file', 'ruleset_schema'])


class TestMain(unittest.TestCase):

    @parameterized.expand([
        ('with_yaml_matching_ruleset', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            HELLO_RULESET_FILE_PATH
        ), SUCCESS),
        ('with_yaml_containing_ruleset_violations', ValidateArgs(
            INVALID_HELLO_YAML_FILE_PATH,
            HELLO_RULESET_FILE_PATH
        ), ERR),
        ('with_ruleset_file_not_found', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            '/test/files/not_found.yamler'
        ), ERR),
        ('with_yaml_data_not_found', ValidateArgs(
            './tests/files/not_found.yaml',
            HELLO_RULESET_FILE_PATH
        ), ERR),
        ('with_empty_yaml_file_path', ValidateArgs(
            '',
            HELLO_RULESET_FILE_PATH
        ), ERR),
        ('with_empty_ruleset_path', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            ''
        ), ERR),
        ('with_invalid_ruleset_extension', ValidateArgs(
            HELLO_YAML_FILE_PATH,
            './test/files/hello.ruleset'
        ), ERR)
    ])
    @patch('argparse.ArgumentParser')
    def test_main(self, name, args, expected_status_code: int, mock_args_parser: Mock):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = args
        mock_args_parser.return_value = mock_parser

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = main()
            self.assertEqual(expected_status_code, status_code)


if __name__ == '__main__':
    unittest.main()
