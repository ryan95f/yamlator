import unittest

from parameterized import parameterized
from collections import namedtuple
from yamler.cmd import validate_yaml_data_from_file
from yamler.exceptions import InvalidRulesetFilenameError

ValidateArgs = namedtuple('ValidateArgs', ['yaml_filepath', 'ruleset_filepath'])


class TestValidateYamlDataFromFile(unittest.TestCase):
    @parameterized.expand([
        ('none_yaml_path', ValidateArgs(None, "./tests/files/hello.yamler"), ValueError),
        ('none_ruleset_path', ValidateArgs("./tests/files/hello.yaml", None), ValueError),
        ('yaml_data_file_not_found', ValidateArgs(
            'not_found.yaml',
            "./tests/files/hello.yamler"
        ), FileNotFoundError),
        ('ruleset_file_not_found', ValidateArgs(
            "./tests/files/hello.yaml",
            "not_found.yamler"
        ), FileNotFoundError),
        ('ruleset_invalid_file_extension', ValidateArgs(
            "./tests/files/hello.yaml",
            "./tests/files/hello.ruleset"
        ), InvalidRulesetFilenameError)
    ])
    def test_validate_yaml_data_from_file_with_invalid_args(self, name: str,
                                                            args: ValidateArgs,
                                                            expected_exception: Exception):  # nopep8
        with self.assertRaises(expected_exception):
            validate_yaml_data_from_file(args.yaml_filepath, args.ruleset_filepath)


if __name__ == '__main__':
    unittest.main()
