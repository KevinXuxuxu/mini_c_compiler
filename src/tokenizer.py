import re
from collections import namedtuple
from exceptions import *

# Token = namedtuple('Token', ['type', 'value'])

class Token:
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "[{}]('{}')".format(type(self).__name__, self.value)

class LITERAL(Token):
    pass

class STRING(LITERAL):
    reg = r'\"[^\n]*?\"'
    token_type = 'STRING'

class CHARACTER(LITERAL):
    reg = r'\'\\0\'|\'\\\\\'|\'\\n\'|\'\\t\'|\'[^\n\\]?\''
    token_type = 'CHARACTER'

class NUMERIC(LITERAL):
    reg = r'\b[0-9]+\b'
    token_type = 'NUMERIC'

class BOOLEAN(LITERAL):
    reg = r'\btrue\b|\bfalse\b'
    token_type = 'BOOLEAN'

class NULL(LITERAL):
    reg = r'\bNULL\b'
    token_type = 'NULL'

class BASE_TYPE(Token):
    reg = r'\bint\b|\bchar\b|\bbool\b|\bvoid\b'
    token_type = 'BASE_TYPE'

class RETURN(Token):
    reg = r'\breturn\b'
    token_type = 'RETURN'

class IF(Token):
    reg = r'\bif\b'
    token_type = 'IF'

class ELSE(Token):
    reg = r'\belse\b'
    token_type = 'ELSE'

class OP(Token):

    # (
    #   oprator_values_iterable,
    #   precedence,  # i.e. operator priority
    #   type, # B: binary, LU: left-unary, RU: right-unary 
    # )
    info_map = [
        ('()#', 0, None),
        # (['++', '--'], 20, 'RU),  # save for special handling
        ('!~', 19, 'LU'),
        ('*/%', 18, 'B'),
        # ('+-', 17, 'B'),  # save for special handling
        (['<<', '>>'], 16, 'B'),
        (['>', '<', '>=', '<='], 15, 'B'),
        (['==', '!='], 14, 'B'),
        ('&', 13, 'B'),
        ('^', 12, 'B'),
        ('|', 11, 'B'),
        (['&&'], 10, 'B'),
        (['||'], 9, 'B')
    ]
    prec = None
    _type = None

    def __str__(self):
        return "[{}]({}, {}, {})".format(type(self).__name__, self.value, self.prec, self._type)

    def get_prec(self):
        if self.prec is None:
            raise ParseException(
                "Trying to get precedence of operator '{}' before generation".format(
                    self.value))
        return self.prec

    def get_type(self):
        if self._type is None:
            raise ParseException(
                "Trying to get type of operator '{}' before generation".format(
                    self.value))
        return self._type

    def gen(self, prev):
        for ops, prec, _type in OP.info_map:
            if self.value in ops:
                self.prec = prec
                self._type = _type
                return self
        raise ParseException("Cannot generate info of operator '{}'".format(self.value))

# fake operator for expression parse
class HASH_OP(OP):
    pass

class O_PAREN(OP):
    reg = r'\('
    token_type = 'O_PAREN'

class C_PAREN(OP):
    reg = r'\)'
    token_type = 'C_PAREN'

class O_BRAC(Token):
    reg = r'{'
    token_type = 'O_BRAC'

class C_BRAC(Token):
    reg = r'}'
    token_type = 'C_BRAC'

class O_SQ_BRAC(Token):
    reg = r'\['
    token_type = 'O_SQ_BRAC'

class C_SQ_BRAC(Token):
    reg = r'\]'
    token_type = 'C_SQ_BRAC'

class COMMENT(Token):
    pass

class S_COMMENT(COMMENT):
    reg = r'\/\/[^\n]*'
    token_type = 'S_COMMENT'

class M_COMMENT(COMMENT):
    # ref: https://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment
    reg = r'(?s)/\*.*?\*/'
    token_type = 'M_COMMENT'

class CREMENT_OP(OP):
    reg = r'\+\+|--'
    token_type = 'CREMENT_OP'

    # ++ -- have the highest precedence and complex occurrence limit
    # Can be after:
    #     Any operand (as right unary operator): a, 12, ... 
    #         (actually should be just variable or function call,
    #         but we'll leave that to typecheck)
    #     Any binary operator (as left unary operator): +, *, ...
    #     Any left unary operator except ++, -- (as left unary operator): !, ...
    #     O_PAREN (as left unary operator)
    # Cannot be after:
    #     Any right unary operator
    #         (which seems to be nothing but ++ and -- themselves)
    #     ++, --
    #     C_PAREN
    #         (only case that it might work is redundent parentheses over variable,
    #         which will be ignored for now)

    def gen(self, prev):
        if prev.value in ['++', '--', ')']:
            raise ParseException("Unexpected {} after {}".format(self.value, prev.value))
        if not isinstance(prev, OP):
            self.prec = 20
            self._type = 'RU'
            return
        self.prec = 19
        self._type = 'LU'

class BITWISE_OP(OP):
    pass

class SHIFT_OP(BITWISE_OP):
    reg = r'<<|>>'
    token_type = 'SHIFT_OP'

class RELA_OP(OP):
    pass

class RELA_OP1(RELA_OP):
    reg = r'==|>=|<=|!='
    token_type = 'RELA_OP1'

class RELA_OP2(RELA_OP):
    reg = r'>|<'
    token_type = 'RELA_OP2'

class LOGICAL_OP(OP):
    reg = r'&&|\|\||!'
    token_type = 'LOGICAL_OP'

class BITWISE_LOGIC_OP(BITWISE_OP):
    reg = r'&|\||\^|~'
    token_type = 'BITWISE_LOGIC_OP'

class ASSIGN_OP(Token):
    reg = r'\+=|-=|\*=|/='
    token_type = 'ASSIGN_OP'

class EQ_ASSIGN_OP(ASSIGN_OP):
    reg = r'='
    token_type = 'EQ_ASSIGN_OP'

class ARITH_OP(OP):
    reg = r'\*|/|%'
    token_type = 'ARITH_OP'

class PLUS_MINUS_OP(ARITH_OP):
    reg = r'\+|-'
    token_type = 'PLUS_MINUS_OP'

    # Binary operator:
    #   after any operand
    #   after C_RARAN
    # Left-unary operator:
    #   after any operator
    #   after O_PAREN 
    def gen(self, prev):
        if isinstance(prev, OP) and not (
                isinstance(prev, C_PAREN) or 
                prev.get_type() == 'RU'):
            self.prec = 19
            self._type = 'LU'
        else:
            self.prec = 17
            self._type = 'B'


class COMMA(Token):
    reg = r','
    token_type = 'COMMA'

class SEMICOLON(Token):
    reg = r';'
    token_type = 'SEMICOLON'

class NAME(Token):
    reg = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    token_type = 'NAME'

class FUNC_CALL(NAME):
    pass

class Tokenizer:

    # TODO: float double
    # TODO: class struct
    # TODO: ternary operator ?:
    # TODO: ref &, deref *, member selection ->
    # TODO: include, macros

    token_list = [
        STRING,
        CHARACTER,
        NUMERIC,
        BOOLEAN,
        NULL,
        BASE_TYPE,
        RETURN,
        IF,
        ELSE,
        O_PAREN,
        C_PAREN,
        O_BRAC,
        C_BRAC,
        O_SQ_BRAC,
        C_SQ_BRAC,
        S_COMMENT,
        M_COMMENT,
        CREMENT_OP,
        SHIFT_OP,
        RELA_OP1,
        RELA_OP2,
        LOGICAL_OP,
        BITWISE_LOGIC_OP,
        ASSIGN_OP,
        EQ_ASSIGN_OP,
        ARITH_OP,
        PLUS_MINUS_OP,
        COMMA,
        SEMICOLON,
        NAME
    ]

    def tokenize(self, code):
        tokens = []
        self.code = code
        while self.code.strip():
            # print(tokens)
            tokens.append(self.tokenize_one())
        return tokens

    def tokenize_one(self):
        self.code = self.code.strip()
        for token_class in self.token_list:
            # print(reg)
            match = re.match(token_class.reg, self.code)
            if match != None:
                match_str = match.group()
                self.code = self.code[len(match_str):]
                return token_class(match_str)
        raise TokenizeFailedException("Tokenize failed at\n" + self.code)
