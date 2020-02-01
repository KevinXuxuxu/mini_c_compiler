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
            while self.match_tokens(BASE_TYPE):
                functions.append(self.parse_func_def())
        except UnexpectedEndOfTokenListException:
            pass
        return Root(functions)
    
    def parse_block(self):
        statements = []
        self.consume(O_BRAC)
        if not self.match_tokens(C_BRAC):
            statements = self.parse_statements()
        self.consume(C_BRAC)
        return Block(statements)
    
    def parse_statements(self):
        statements = []
        while not self.match_tokens(C_BRAC):
            statements.append(self.parse_statement())
        return statements
    
    def parse_statement(self):
        statement = None
        if self.match_tokens(NAME, ASSIGN_OP):
            statement = self.parse_assignment()
        elif self.match_tokens(BASE_TYPE, NAME, O_PAREN):
            return self.parse_func_def()
        elif self.match_tokens(BASE_TYPE, NAME):
            statement = self.parse_var_def()
        elif self.match_tokens(IF):
            return self.parse_if()
        elif self.match_tokens(RETURN):
            statement = self.parse_return()
        else:
            statement = self.parse_expr()
        # TODO: add control flows (if, for, while, ...)
        self.consume(SEMICOLON)
        return statement
    
    def parse_assignment(self):
        return Assignment(
            self.parse_var_ref(),
            self.consume(ASSIGN_OP).value,
            self.parse_expr())
    
    def parse_func_def(self):
        return FuncDef(
            self.consume(BASE_TYPE).value,
            self.consume(NAME).value,
            self.parse_args(),
            self.parse_block())
    
    def parse_return(self):
        self.consume(RETURN)
        if not self.match_tokens(SEMICOLON):
            return Return(self.parse_expr())
        return Return(None)
    
    def consume(self, expected_type=None):
        self.parse_comment()
        if not expected_type or isinstance(self.tokens[0], expected_type):
            return self.tokens.pop(0)
        raise ParseException(
            "Expecting token of type '{}' but got '{}'".format(
                expected_type, type(self.tokens[0])))
    
    def match_tokens(self, *argv):
        try:
            self.parse_comment()
            for i, _type in enumerate(argv):
                if not isinstance(self.tokens[i], _type):
                    return False
            return True
        except IndexError:
            # TODO: add expecting token type to exception message
            raise UnexpectedEndOfTokenListException()
    
    def parse_args(self):
        args = []
        self.consume(O_PAREN)
        if self.match_tokens(BASE_TYPE):
            args.append(self.parse_var_def())
            while self.match_tokens(COMMA):
                self.consume(COMMA)
                args.append(self.parse_var_def())
        self.consume(C_PAREN)
        return args

    def parse_var_name(self):
        _type = self.consume(BASE_TYPE).value
        name = self.consume(NAME).value
        if self.match_tokens(O_SQ_BRAC):
            self.consume(O_SQ_BRAC)
            if self.match_tokens(C_SQ_BRAC):
                self.consume(C_SQ_BRAC)
                return name, _type, '*'
            else:
                expr = self.parse_expr()
                self.consume(C_SQ_BRAC)
                return name, _type, expr
        return name, _type, None

    def parse_default(self):
        if self.match_tokens(O_BRAC):
            self.consume(O_BRAC)
            default = [self.parse_expr()]
            while self.match_tokens(COMMA):
                self.consume(COMMA)
                default.append(self.parse_expr())
            self.consume(C_BRAC)
            return default
        return self.parse_expr()

    def parse_var_def(self):
        name, _type, _len = self.parse_var_name()
        default = None
        if self.match_tokens(EQ_ASSIGN_OP):
            self.consume(EQ_ASSIGN_OP)
            default = self.parse_default()
        return VarDef(name, _type, _len, default)

    def get_postfix(self):
        stack = [HASH_OP('#').gen(None)]
        postfix = []
        prev = stack[0]
        while True:
            if self.match_tokens(NAME) or self.match_tokens(LITERAL):
                t = self.consume()
                postfix.append(t)
                prev = t
            elif self.match_tokens(O_PAREN):
                if isinstance(prev, NAME):
                    # replace previous NAME with FUNC_CALL
                    postfix[-1] = FUNC_CALL(self.parse_func_call(prev.value))
                else:
                    t = self.consume()
                    t.gen(prev)
                    stack.append(t)
                    prev = t
            elif self.match_tokens(C_PAREN):
                while not isinstance(stack[-1], O_PAREN):
                    if isinstance(stack[-1], HASH_OP):
                        return postfix
                    postfix.append(stack.pop())
                stack.pop()  # pop out O_PAREN
                prev = self.consume()
            elif self.match_tokens(OP):
                op = self.consume()
                op.gen(prev)
                op_prec, top_prec = op.get_prec(), stack[-1].get_prec()
                if op_prec > top_prec or (
                        op_prec == top_prec and op.get_type() == 'LU'):
                    pass
                else:
                    while op_prec <= stack[-1].get_prec():
                        postfix.append(stack.pop())
                stack.append(op)
                prev = op
            else:
                break
        while not isinstance(stack[-1], HASH_OP):
            postfix.append(stack.pop())
        return postfix
    
    def to_operand(self, t):
        if isinstance(t, LITERAL):
            return self.parse_literal_internal(t)
        if isinstance(t, NAME):
            if isinstance(t.value, FuncCall):
                return t.value
            return VarRef(t.value)
        return t
    
    def to_unary_op(self, t):
        if isinstance(t, CREMENT_OP):
            return t.get_type()[0] + t.value
        return t.value
    
    def build_expr(self, postfix):
        stack = []
        for t in postfix:
            if isinstance(t, LITERAL) or isinstance(t, NAME):
                stack.append(self.to_operand(t))
            elif isinstance(t, OP):
                if t.get_type() == 'B':
                    stack.append(BinaryOp(t.value, stack.pop(), stack.pop()))
                elif t.get_type() in ['LU', 'RU']:
                    stack.append(UnaryOp(self.to_unary_op(t), stack.pop()))
                else:
                    raise ExpressionParseException(
                        "Unrecognized operator type {} from operator {}".format(
                            t.get_type(), t.value))
            else:
                raise ExpressionParseException(
                    "Unexpected token type: {}".format(type(t).__name__))
        if len(stack) != 1:
            raise ExpressionParseException(
                "Unfinished expression parse\n    stack: {}".format(stack))
        return stack[0]

    def parse_expr(self):
        return self.build_expr(self.get_postfix())

    def parse_func_call(self, name=None):
        if name is None:
            name = self.consume(NAME).value
        params = self.parse_params()
        return FuncCall(name, params)
    
    def parse_params(self):
        params = []
        self.consume(O_PAREN)
        if not self.match_tokens(C_PAREN):
            params.append(self.parse_expr())
        while self.match_tokens(COMMA):
            self.consume()
            params.append(self.parse_expr())
        self.consume(C_PAREN)
        return params
    
    # Standard C does not support default value for parameters
    # def parse_param(self):
    #     name = None
    #     if self.match_tokens(NAME, EQ_ASSIGN_OP):
    #         name = self.parse_var_ref()
    #         self.consume(EQ_ASSIGN_OP)
    #     return Param(name, self.parse_expr())

    def parse_var_ref(self):
        return VarRef(self.consume(NAME).value)

    def parse_literal(self):
        if self.match_tokens(LITERAL):
            return self.parse_literal_internal(self.consume(LITERAL))

    def parse_literal_internal(self, token):
        v = token.value
        if isinstance(token, NUMERIC):
            return Literal('int', int(v))
        if isinstance(token, STRING):
            return Literal('string', eval(v))
        if isinstance(token, CHARACTER):
            return Literal('char', eval(v))
        if isinstance(token, BOOLEAN):
            return Literal('bool', v == 'true')
        if isinstance(token, NULL):
            return Literal('null', None)
        raise ParseException("Unrecognized literal {} of token type {}".format(
            self.tokens[0].value, type(self.tokens[0])))

    def parse_comment(self):
        while isinstance(self.tokens[0], COMMENT):
            self.tokens.pop(0)

    def parse_if(self):
        self.consume(IF)
        self.consume(O_PAREN)
        cond = self.parse_expr()
        self.consume(C_PAREN)
        true_body = None
        if self.match_tokens(O_BRAC):
            true_body = self.parse_block()
        else:
            true_body = Block([self.parse_statement()])
        false_body = None
        if self.match_tokens(ELSE):
            self.consume()
            if self.match_tokens(O_BRAC):
                false_body = self.parse_block()
            else:
                false_body = Block([self.parse_statement()])
        return If(cond, true_body, false_body)
