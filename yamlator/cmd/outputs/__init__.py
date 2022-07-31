"""Shortcuts for accessing display options"""

from yamlator.cmd.outputs.base import SuccessCode
from yamlator.cmd.outputs.json_output import JSONOutput
from yamlator.cmd.outputs.table_output import TableOutput
from yamlator.cmd.outputs.yaml_output import YAMLOutput


__all__ = [
    'SuccessCode',
    'JSONOutput',
    'TableOutput',
    'YAMLOutput',
]
