"""Display output class for generating JSON"""
import json
from typing import Iterator

from yamlator.violations import Violation
from yamlator.violations import ViolationJSONEncoder
from yamlator.cmd.outputs.base import SuccessCode
from yamlator.cmd.outputs.base import ViolationOutput


class JSONOutput(ViolationOutput):
    """Displays violations as JSON"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user as JSON

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

        violation_count = len(violations)
        pre_json_data = {
            'violations': violations,
            'violations_count': violation_count
        }

        json_data = json.dumps(pre_json_data,
                               cls=ViolationJSONEncoder, indent=4)
        print(json_data)

        return SuccessCode.SUCCESS if violation_count == 0 else SuccessCode.ERR
