import argparse

from .utils import load_yaml_file
from .utils import load_yamler_ruleset
from .parser import YamlerParser
from .wranglers import wrangle_data


def _create_args_parser():
    description = "Validate if a YAML file matches a ruleset schema"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("file", type=str,
                        help="The file to be validated")
    parser.add_argument("--schema", dest="ruleset_schema", required=True,
                        help="The schama that will be used to validate the file")
    return parser


def main():
    parser = _create_args_parser()
    args = parser.parse_args()

    yaml_data = load_yaml_file(args.file)
    ruleset = load_yamler_ruleset(args.ruleset_schema)

    parser = YamlerParser()
    tokens = parser.parse(ruleset)

    violations = wrangle_data(yaml_data, tokens)

    violation_count = len(violations)
    print("\n{:<4} violation(s) found".format(violation_count))

    if len(violations) > 0:
        print("\n{:<30} {:<20} {:<15} {:20}".format(
                "Parent Key", "Key", "Violation", "Message"))
        print("---------------------------------------------------------------------------")  # nopep8
        for violation in violations:
            print("{:<30} {:<20} {:<15} {:20}".format(
                violation.parent,
                violation.key,
                violation.violation_type,
                violation.message))
        print("---------------------------------------------------------------------------")  # nopep8


if __name__ == '__main__':
    main()
