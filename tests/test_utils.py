import unittest
from yamler.utils import load_yaml_file


class TestLoadYamlFile(unittest.TestCase):
    def test_yaml_file_invalid_filename(self):
        filenames = [None, ""]

        for filename in filenames:
            with self.assertRaises(ValueError):
                load_yaml_file(filename)

    def test_yaml_file_with_successful_read(self):
        yaml_file = "tests/yaml/hello.yaml"
        results = load_yaml_file(yaml_file)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
