from collections import namedtuple
from tokenizer import *
from tree import *
from exceptions import *

class Parser:
    
    def parse(self, tokens):
        self.tokens = tokens
        tree = self.parse_root()
        return tree
    
    def parse_root(self):
        functions = []
        try:
            while self.next_token_is(BASE_TYPE):
                functions.append(self.parse_func_def())
        except UnexpectedEndOfTokenListException:
            pass
        return Root(functions)
    
    def parse_func_def(self):
        _type = self.consume(BASE_TYPE).value
        name = self.consume(NAME).value
        args = self.parse_args()
        self.consume(O_BRAC)
        body = self.parse_expr()
        self.consume(C_BRAC)
        return FuncDef(name, _type, args, body)
    
    def consume(self, expected_type):
        if isinstance(self.tokens[0], expected_type):
            return self.tokens.pop(0)
        raise ParseException(
            "Expecting token of type '{}' but got '{}'".format(
                expected_type, type(self.tokens[0])))
    
    def next_token_is(self, _type):
        try:
            return isinstance(self.tokens[0], _type)
        except IndexError:
            # TODO: add expecting token type to exception message
            raise UnexpectedEndOfTokenListException()
    
    def parse_args(self):
        args = []
        self.consume(O_PARAN)
        if self.next_token_is(BASE_TYPE):
            args.append(self.parse_var_def())
            while self.next_token_is(COMMA):
                self.consume(COMMA)
                args.append(self.parse_var_def())
        self.consume(C_PARAN)
        return args
    
    def parse_var_def(self):
        _type = self.consume(BASE_TYPE).value
        name = self.consume(NAME).value
        default = None
        if self.next_token_is(EQ_ASSIGN_OP):
            self.consume(EQ_ASSIGN_OP)
            default = self.parse_literal()
        return VarDef(name, _type, default)
    
    def parse_expr(self):
        return self.parse_literal()

    def parse_literal(self):
        if self.next_token_is(NUMERIC):
            return Literal('int', int(self.consume(NUMERIC).value))
        if self.next_token_is(STRING):
            return Literal('string', eval(self.consume(STRING).value))
        if self.next_token_is(CHARACTER):
            return Literal('char', eval(self.consume(CHARACTER).value))
        if self.next_token_is(BOOLEAN):
            return Literal('bool', self.consume(BOOLEAN).value == 'true')
        if self.next_token_is(NULL):
            self.consume(NULL)
            return Literal('null', None)
        raise ParseException("Unrecognized literal {} of token type {}".format(
            self.tokens[0].value, type(self.tokens[0])))
