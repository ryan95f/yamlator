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

    print("=================================")
    if len(violations) == 0:
        print("No Violations")
    else:
        print("Violation Report")
        print("=================================")

    for violation in violations.values():
        for v in violation:
            print(v.message)
    print("=================================")


if __name__ == '__main__':
    main()
