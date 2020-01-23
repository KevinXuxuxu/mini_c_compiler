import re
from collections import namedtuple

class TokenizeFailedException(Exception):
    pass

Token = namedtuple('Token', ['type', 'value'])

class Tokenizer:

    # TODO: float double
    # TODO: class struct
    # TODO: ternary operator ?:
    # TODO: ref &, deref *, member selection ->
    # TODO: include, macros

    token_list = [
        ('STRING_LITERAL', r'\"[^\n]*?\"'),
        ('CHARACTER', r'\'\\0\'|\'\\\\\'|\'\\n\'|\'\\t\'|\'[^\n\\]?\''),
        ('NUMERIC', r'\b[0-9]+\b'),
        ('BOOLEAN', r'\btrue\b|\bfalse\b'),
        ('BASE_TYPE', r'\bint\b|\bchar\b|\bbool\b|\bvoid\b'),
        ('RETURN', r'\breturn\b'),
        ('O_PARAN', r'\('),
        ('C_PARAN', r'\)'),
        ('O_BRAC', r'{'),
        ('C_BRAC', r'}'),
        ('O_SQ_BRAC', r'\['),
        ('C_SQ_BRAC', r'\]'),
        ('S_COMMENT', r'\/\/[^\n]*'),
        # ref: https://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment
        ('M_COMMENT', r'(?s)/\*.*?\*/'),
        ('CREMENT_OP', r'\+\+|--'),
        ('BITWISE_OP', r'<<|>>'),
        ('RELA_OP', r'==|>|<|>=|<=|!='),
        ('LOGICAL_OP', r'&&|\|\||!'),
        ('BITWISE_OP', r'&|\||\^|~'),
        ('ASSIGN_OP', r'=|\+=|-=|\*=|/='),
        ('ARITH_OP', r'\+|-|\*|/|%'),
        ('COMMA', r','),
        ('SEMICOLON', r';'),
        ('NAME', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
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
        for _type, reg in self.token_list:
            # print(reg)
            match = re.match(reg, self.code)
            if match != None:
                match_str = match.group()
                self.code = self.code[len(match_str):]
                return Token(_type, match_str)
        raise TokenizeFailedException("Tokenize failed at\n" + self.code)
