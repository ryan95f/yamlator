import unittest

from parameterized import parameterized
from collections import namedtuple
from src.cmd import validate_yaml_data_from_file
from src.exceptions import InvalidSchemaFilenameError

VALID_YAML_DATA_FILE_PATH = './tests/files/hello.yaml'
VALID_RULESET_FILE_PATH = './tests/files/hello.yamler'

ValidateArgs = namedtuple('ValidateArgs', ['yaml_filepath', 'ruleset_filepath'])


class TestValidateYamlDataFromFile(unittest.TestCase):
    @parameterized.expand([
        ('none_yaml_path', ValidateArgs(None, VALID_RULESET_FILE_PATH), ValueError),
        ('none_ruleset_path', ValidateArgs(VALID_YAML_DATA_FILE_PATH, None), ValueError),
        ('yaml_data_file_not_found', ValidateArgs(
            'not_found.yaml',
            VALID_RULESET_FILE_PATH
        ), FileNotFoundError),
        ('ruleset_file_not_found', ValidateArgs(
            VALID_YAML_DATA_FILE_PATH,
            'not_found.yamler'
        ), FileNotFoundError),
        ('ruleset_invalid_file_extension', ValidateArgs(
            VALID_YAML_DATA_FILE_PATH,
            './tests/files/hello.ruleset'
        ), InvalidSchemaFilenameError)
    ])
    def test_validate_yaml_data_from_file_with_invalid_args(self, name: str,
                                                            args: ValidateArgs,
                                                            expected_exception: Exception):  # nopep8
        with self.assertRaises(expected_exception):
            validate_yaml_data_from_file(args.yaml_filepath, args.ruleset_filepath)

    def test_validate_yaml_data_from_file_with_valid_data(self):
        violations = validate_yaml_data_from_file(
            yaml_filepath=VALID_YAML_DATA_FILE_PATH,
            yamler_filepath=VALID_RULESET_FILE_PATH
        )
        self.assertIsNotNone(violations)


if __name__ == '__main__':
    unittest.main()
