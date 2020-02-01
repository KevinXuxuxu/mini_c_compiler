import sys
from tokenizer import Tokenizer
from parser import Parser
from validator import Validator


def main():
    code = open(sys.argv[1]).read()
    T = Tokenizer()
    tokens = T.tokenize(code)
    for t in tokens:
        print(t)

    P = Parser()
    tree = P.parse(tokens)
    # print(tree)
    print(tree.to_str())

    tree.validate()

if __name__ == '__main__':
    main()
