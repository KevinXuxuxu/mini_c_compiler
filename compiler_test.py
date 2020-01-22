import pytest
from compiler import *

T = Tokenizer()

def run_test_cases(test_cases):
    for _input, expected in test_cases.items():
        if isinstance(expected, Exception):
            with pytest.raises(type(expected)) as excinfo:
                T.tokenize(_input)
            assert str(excinfo.value) == expected.args[0]
        else:
            assert T.tokenize(_input) == expected, "failing"

def test_tokenizer_basic():
    test_cases = {
        'int func(int a, int b) { func2(); }': ['int', 'func', '(', 'int', 'a', ',', 'int', 'b', ')', '{', 'func2', '(', ')', ';', '}']
    }
    run_test_cases(test_cases)

def test_tokenizer_string():
    test_cases = {
        """ "sfe 'ewr' wer 123" 123 de 'dfe ;sdfe; ' """: ['"sfe \'ewr\' wer 123"', '123', 'de', "'dfe ;sdfe; '"],
        """ 'sfe "ewr" wer 123' 123 de "dfe ;sdfe; " """: ['\'sfe "ewr" wer 123\'', '123', 'de', '"dfe ;sdfe; "'],
        """ 'sdf " sdfs 123; 232' sdffe" sfefe123()' we " """: ['\'sdf " sdfs 123; 232\'', 'sdffe', '" sfefe123()\' we "'],
        """ 'sdfe\nsdfef; eff' """: TokenizeFailedException("Unrecognized charactor '")
    }
    run_test_cases(test_cases)
