import pytest

from tokenizer import *
from exceptions import *

T = Tokenizer()

def run_test_cases(test_cases):
    for _input, expected in test_cases.items():
        if isinstance(expected, Exception):
            with pytest.raises(type(expected)):
                T.tokenize(_input)
        else:
            result = T.tokenize(_input)
            for i, t in enumerate(result):
                assert type(t) == expected[i][0]
                assert t.value == expected[i][1]

def test_basic():
    test_cases = {
        'int func(int a, int b) { func2(); }': [
            (BASE_TYPE, 'int'),
            (NAME, 'func'),
            (O_PAREN, '('),
            (BASE_TYPE, 'int'),
            (NAME, 'a'),
            (COMMA, ','),
            (BASE_TYPE, 'int'),
            (NAME, 'b'),
            (C_PAREN, ')'),
            (O_BRAC, '{'),
            (NAME, 'func2'),
            (O_PAREN, '('),
            (C_PAREN, ')'),
            (SEMICOLON, ';'),
            (C_BRAC, '}')
        ]
    }
    run_test_cases(test_cases)

def test_string():
    test_cases = {
        """ "sfe 'ewr' wer 123"\n123 de 'd' """: [
            (STRING, '"sfe \'ewr\' wer 123"'),
            (NUMERIC, '123'),
            (NAME, 'de'),
            (CHARACTER, "'d'")
        ],
        """ 'sfe "ewr" wer 123' 123 de "dfe ;sdfe; " """: TokenizeFailedException(),
        """ "sdfe\nsdfef; eff" """: TokenizeFailedException()
    }
    run_test_cases(test_cases)

def test_numeric():
    test_cases = {
        "123 t34\n56": [
            (NUMERIC, '123'),
            (NAME, 't34'),
            (NUMERIC, '56')
        ],
        # float is not supported yet
        "123.4567": TokenizeFailedException()
    }
    run_test_cases(test_cases)