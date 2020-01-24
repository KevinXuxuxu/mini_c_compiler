from collections import namedtuple
from tree import *

class ParseException(Exception):
    pass

class Parser:
    
    def parse(self, tokens):
        self.tokens = tokens
        tree = self.parse_func_def()
        return tree
    
    def parse_func_def(self):
        _type = self.consume('BASE_TYPE').value
        name = self.consume('NAME').value
        args = self.parse_args()
        self.consume('O_BRAC')
        body = self.parse_expr()
        self.consume('C_BRAC')
        return FuncDef(name, _type, args, body)
    
    def consume(self, expected_type):
        if self.tokens[0].type == expected_type:
            return self.tokens.pop(0)
        raise ParseException(
            "Expecting token of type '{}' but got '{}'".format(
                expected_type, self.tokens[0].type))
    
    def peek(self):
        return self.tokens[0]
    
    def parse_args(self):
        args = []
        self.consume('O_PARAN')
        if self.peek().type == 'BASE_TYPE':
            args.append(self.parse_var())
            while self.peek().type == 'COMMA':
                self.consume('COMMA')
                args.append(self.parse_var())
        self.consume('C_PARAN')
        return args
    
    def parse_var(self):
        _type = self.consume('BASE_TYPE').value
        name = self.consume('NAME').value
        default = None
        if self.peek().type == 'ASSIGN_OP' and self.peek().value == '=':
            self.consume('ASSIGN_OP')
            default = self.parse_literal()
        return Variable(name, _type, default)
    
    def parse_expr(self):
        return self.parse_literal()

    def parse_literal(self):
        top = self.peek()
        if top.type == 'NUMERIC':
            return Literal('int', int(self.consume('NUMERIC').value))
        if top.type == 'STRING_LITERAL':
            return Literal('string', eval(self.consume('STRING_LITERAL').value))
        if top.type == 'CHARACTER':
            return Literal('char', eval(self.consume('CHARACTER').value))
        if top.type == 'BOOLEAN':
            return Literal('bool', self.consume('BOOLEAN').value == 'true')
        raise ParseException("Unrecognized literal {} of token type {}".format(top.value, top.type))
