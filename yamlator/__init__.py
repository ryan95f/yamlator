"""Shortcuts for accessing common Yamlator functions"""

from yamlator.validators.core import validate_yaml
from yamlator.cmd import validate_yaml_data_from_file

__all__ = [
    'validate_yaml',
    'validate_yaml_data_from_file'
]
