from yamler.utils import load_yaml_file
from yamler.utils import load_yamler_ruleset
from yamler.parser import YamlerParser
from yamler.wrangler import YamlerWrangler, RuleBuilder

EXAMPLE_RULESET = "example/hello.yamler"

def main():
    yaml_data = load_yaml_file("example/hello.yaml")
    ruleset = load_yamler_ruleset(EXAMPLE_RULESET)

    parser = YamlerParser()
    tokens = parser.parse(ruleset)

    builder = RuleBuilder(tokens)

    wrangler = YamlerWrangler(builder.rules)
    violations = wrangler.wrangle(yaml_data)

    print("=================================")
    if len(violations) == 0:
        print("No Violations")

    for idx, (key, message) in enumerate(violations.items()):
        print(message)
    print("=================================")

if __name__ == '__main__':
    main()
