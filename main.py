from yamler.utils import load_yaml_file
from yamler.utils import load_yamler_ruleset
from yamler.parser import YamlerParser
from yamler.wrangler import YamlerWrangler

EXAMPLE_RULESET = "example/hello.yamler"
TEST_YAML_FILE = "example/hello.yaml"


def main():
    yaml_data = load_yaml_file(TEST_YAML_FILE)
    ruleset = load_yamler_ruleset(EXAMPLE_RULESET)

    parser = YamlerParser()
    tokens = parser.parse(ruleset)

    wrangler = YamlerWrangler(tokens)
    violations = wrangler.wrangle(yaml_data)

    violation_count = len(violations)
    print("\n{:<4} violation(s) found".format(violation_count))

    if len(violations) > 0:
        print("\n{:<15} {:20}".format("Violation", "Message"))
        print("-----------------------------------------")
        for violation in violations.values():
            for v in violation:
                print("{:<15} {:20}".format(v.violation_type, v.message))
        print("-----------------------------------------")


if __name__ == '__main__':
    main()
