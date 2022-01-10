from yamler.utils import load_yamler_ruleset
from yamler.parser import YamlerParser

EXAMPLE_RULESET = "example/hello.yamler"

def main():
    ruleset = load_yamler_ruleset(EXAMPLE_RULESET)
    
    parser = YamlerParser()
    tokens = parser.parse(ruleset)
    print(tokens)



if __name__ == '__main__':
    main()
