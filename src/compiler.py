import sys
from tokenizer import Tokenizer
from parser import Parser


def main():
    code = open(sys.argv[1]).read()

    # Tokenize
    T = Tokenizer()
    tokens = T.tokenize(code)
    for t in tokens:
        print(t)

    # Parse
    P = Parser()
    tree = P.parse(tokens)

    # Validate
    tree.validate()
    print(tree.to_str())

if __name__ == '__main__':
    main()
