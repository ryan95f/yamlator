"""Display output class for generating YAML"""
import yaml

from collections import deque
from typing import Iterator

from yamlator.violations import Violation
from yamlator.cmd.outputs.base import SuccessCode
from yamlator.cmd.outputs.base import ViolationOutput

from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import BuiltInTypeViolation
from yamlator.violations import RulesetTypeViolation
from yamlator.violations import RegexTypeViolation


class YAMLOutput(ViolationOutput):
    """Display violations as YAML"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user as YAML

        Args:
            violations (Iterator[Violation]): A collection
            of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found

        Raises:
            ValueError: If the violations list is None
        """

        if violations is None:
            raise ValueError('violations should not be None')

        YAMLOutput._set_up_dumper()

        violation_count = len(violations)
        data = {
            'violations': violations,
            'violationCount': violation_count
        }

        yaml_str = yaml.dump(data)
        print(yaml_str)
        return SuccessCode.SUCCESS if violation_count == 0 else SuccessCode.ERR

    @staticmethod
    def _set_up_dumper() -> None:
        yaml.add_representer(deque, YAMLOutput._deque_dumper)
        yaml.add_representer(RequiredViolation, YAMLOutput._violation_dumper)
        yaml.add_representer(TypeViolation, YAMLOutput._violation_dumper)
        yaml.add_representer(BuiltInTypeViolation, YAMLOutput._violation_dumper)
        yaml.add_representer(RulesetTypeViolation, YAMLOutput._violation_dumper)
        yaml.add_representer(RegexTypeViolation, YAMLOutput._violation_dumper)

    @staticmethod
    def _deque_dumper(dumper: yaml.Dumper, data: deque) -> yaml.SequenceNode:
        return dumper.represent_list(data)

    @staticmethod
    def _violation_dumper(dumper: yaml.Dumper,
                          data: Violation) -> yaml.SequenceNode:
        data_dict = {
            'key': data.key,
            'parent': data.parent,
            'message': data.message,
            'violationType': data.violation_type
        }
        return dumper.represent_dict(data_dict)
