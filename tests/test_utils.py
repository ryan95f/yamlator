import unittest
from yaml import load
from yamler.utils import load_yaml_file


class TestLoadYamlFile(unittest.TestCase):
    def test_yaml_file_invalid_filename(self):
        filenames = [None, ""]

        for filename in filenames:
            with self.assertRaises(ValueError):
                load_yaml_file(filename)


if __name__ == '__main__':
    unittest.main()
