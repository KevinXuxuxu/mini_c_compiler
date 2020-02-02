"""
                 v .   ._, |_  .,
           `-._\/  .  \ /    |/_
               \\  _\, y | \//
         _\_.___\\, \\/ -.\||
           `7-,--.`._||  / / ,
           /'     `-. `./ / |/_.'
                     |    |//
                     |_    /
                     |-   |
                     |   =|
                     |    |
--------------------/ ,  . \--------._
"""

from collections import namedtuple
from random import randint
from utils import unescape
from exceptions import *

class Context(namedtuple('Context', ['id', 'type', 'parent', 'v_map', 'f_map'])):
    returned = False
    
    def __repr__(self):
        return "C({}, {} , {}, {}, {})".format(
            self.id,
            self.type,
            self.parent.id if self.parent else "None",
            self.v_map.keys(),
            self.f_map.keys())
    
    def get_var(self, name):
        c = self
        while c is not None and name not in c.v_map:
            c = c.parent
        if c is None:
            raise UndefinedVariableException(name)
        return c.v_map[name]
    
    def get_func(self, name):
        c = self
        while c is not None and name not in c.f_map:
            c = c.parent
        if c is None:
            raise UndefinedFunctionException(name)
        return c.f_map[name]
    
    def get_return_target(self):
        c = self
        while c != None and c.type is None:
            c = c.parent
        if c is None:
            raise UnexpectedReturnException()
        return c
    
    @classmethod
    def new(cls, _type, parent):
        return Context(randint(1, 1000000), _type, parent, {}, {})


class Tree:
    """ This is an interface"""
    unit = ' '*3
    extra_fields = []
    
    def to_str(self, i=1):
        s = "{}:\n".format(type(self).__name__)
        for field in list(self._fields) + self.extra_fields:
            value = self.__getattribute__(field)
            if isinstance(value, Tree):
                s += "{}{}:{}".format(
                    self.unit * i,
                    field,
                    value.to_str(i+1)
                )
            elif isinstance(value, list):
                s += "{}{}:\n".format(self.unit * i, field)
                for v in value:
                    if isinstance(v, Tree):
                        s += "{}- {}".format(self.unit * i, v.to_str(i+1))
                    else:
                        s += "{}- {}\n".format(self.unit * i, unescape(v))
            else:
                s += "{}{}: {}\n".format(self.unit * i, field, unescape(value))
        return s
    
    def validate(self, ctx):
        pass


class Root(namedtuple('Root', ['functions']), Tree):
    
    def validate(self, ctx=Context(0, None, None, {}, {})):
        for f in self.functions:
            f.validate(ctx)

class FuncDef(namedtuple('FuncDef', ['type', 'name', 'args', 'body']), Tree):
    
    def validate(self, ctx):
        name, _type = self.name, self.type
        if name in ctx.f_map:
            raise FunctionDefDuplication(name)
        ctx.f_map[name] = (_type, [v.type for v in self.args])
        new_ctx = Context.new(_type, ctx)
        for v in self.args:
            has_default = v.validate(new_ctx)
            if has_default:
                raise DefaultParameterInFunctionDef(name, v.name)
        self.body.validate(new_ctx)
        if _type != 'void' and not new_ctx.returned:
            raise UnreturnedFunctionException(name)

class Literal(namedtuple('Literal', ['type', 'value']), Tree):
    pass

class Typable(Tree):
    type = None
    extra_fields = ['type']

class VarDef(namedtuple('VarDef', ['name', 'type', 'default']), Tree):

    extra_fields = ['len']

    def set_len(self, _len):
        self.len = _len
        return self

    def validate_len(self, ctx):
        _len = self.len
        if _len is not None and _len != '*':
            _len.validate(ctx)
            if _len.type != 'int':
                raise TypeMismatchException('int', _len.type)
            if isinstance(_len, Literal):
                l = int(_len.value)
                if self.default != None and l < len(self.default):
                    raise ArrayInitializeException(self.name, l, len(self.default))
                self.len = l
    
    def validate(self, ctx):
        name, _type, _len, default = self.name, self.type, self.len, self.default
        if name in ctx.v_map:
            raise VariableDefDuplication(name)
        if _len is None:
            if default != None:
                default.validate(ctx)
                if default.type != _type:
                    raise TypeMismatchException(_type, default.type)
        else:
            if default is None:
                if _len == '*':
                    raise ArrayTypeException(name)
                self.validate_len(ctx)
            elif isinstance(default, list):
                for expr in default:
                    expr.validate(ctx)
                    if expr.type != _type:
                        raise TypeMismatchException(_type, expr.type)
                if _len == '*':
                    self.len = len(default)
                else:
                    self.validate_len(ctx)
        ctx.v_map[name] = (_type, _len is not None)
        return default != None

class VarRef(namedtuple('VarRef', ['name']), Typable):
    
    def validate(self, ctx):
        self.type, _ = ctx.get_var(self.name)

class Operator(Typable):
    pass

class UnaryOp(namedtuple('UnaryOp', ['op', 'child']), Operator):
    type_map = {
        '+': ['int'],
        '-': ['int'],
        'R++': ['int'],
        'R--': ['int'],
        'L++': ['int'],
        'L--': ['int'],
        '!': ['bool'],
        '~': ['int']
    }

    def check_type(self):
        c_type, allowed = self.child.type, self.type_map[self.op]
        if c_type not in allowed:
            return TypeMismatchException(allowed, c_type)
        self.type = c_type
    
    def validate(self, ctx):
        self.child.validate(ctx)
        self.check_type()

class BinaryOp(namedtuple('BinaryOp', ['op', 'right', 'left']), Operator):
    type_map = {
        '+': ['int', 'string'],
        '-': ['int'],
        '*': ['int'],
        '/': ['int'],
        '%': ['int'],
        '<<': ['int', 'bool'],
        '>>': ['int', 'bool'],
        '>': ['int'],
        '<': ['int'],
        '>=': ['int'],
        '<=': ['int'],
        '==': '*',
        '!=': '*',
        '&': ['int'],
        '^': ['int'],
        '|': ['int'],
        '&&': ['bool'],
        '||': ['bool'],
        '=': '*'
    }

    logic_ops = ['>', '<', '>=', '<=', '!=', '==', '&&', '||']
    
    def check_type(self):
        l_type, r_type, allowed = self.left.type, self.right.type, self.type_map[self.op]
        if allowed != '*' and l_type not in allowed:
            raise TypeMismatchException(allowed, l_type)
        if r_type != l_type:
            raise TypeMismatchException(l_type, r_type)
        # TODO: is there a more generic way to do this?
        if self.op in self.logic_ops:
            self.type = 'bool'
        else:
            self.type = l_type
    
    def validate(self, ctx):
        self.left.validate(ctx)
        self.right.validate(ctx)
        self.check_type()

class FuncCall(namedtuple('FuncCall', ['name', 'params']), Typable):
    
    def validate(self, ctx):
        self.type, v_types = ctx.get_func(self.name)
        params = self.params
        if len(params) != len(v_types):
            raise WrongNumberOfArguments(self.name, len(v_types), len(params))
        for i, expr in enumerate(params):
            expr.validate(ctx)
            if v_types[i] != expr.type:
                raise TypeMismatchException(v_types[i], expr.type)

class ArrayRef(namedtuple('ArrayRef', ['name', 'index']), Typable):

    def validate(self, ctx):
        self.type, is_array = ctx.get_var(self.name)
        if not is_array:
            raise NotAnArrayException(self.name)
        self.index.validate(ctx)
        if self.index.type != 'int':
            raise TypeMismatchException('int', self.index.type)

# class Param(namedtuple('Param', ['name', 'expr']), Tree):
#     pass

class Block(namedtuple('Block', ['statements']), Tree):

    def validate(self, ctx):
        for st in self.statements:
            st.validate(ctx)

class Assignment(namedtuple('Assignment', ['var_ref', 'op', 'expr']), Tree):

    def validate(self, ctx):
        self.var_ref.validate(ctx)
        self.expr.validate(ctx)
        BinaryOp(self.op[0], self.expr, self.var_ref).check_type()

class Return(namedtuple('Return', ['expr']), Tree):

    def validate(self, ctx):
        target_ctx = ctx.get_return_target()
        if self.expr == None:
            if target_ctx.type != 'void':
                raise TypeMismatchException(target_ctx.type, 'void')
        else:
            self.expr.validate(ctx)
            if target_ctx.type != self.expr.type:
                raise TypeMismatchException(target_ctx.type, self.expr.type)
        target_ctx.returned = True

class If(namedtuple('If', ['cond', 'true_body', 'false_body']), Tree):
    
    def validate(self, ctx):
        cond = self.cond
        cond.validate(ctx)
        if cond.type != 'bool':
            raise TypeMismatchException('bool', cond.type)
        self.true_body.validate(Context.new(None, ctx))
        if self.false_body != None:
            self.false_body.validate(Context.new(None, ctx))

class While(namedtuple('While', ['cond', 'body']), Tree):
    
    def validate(self, ctx):
        cond = self.cond
        cond.validate(ctx)
        if cond.type != 'bool':
            raise TypeMismatchException('bool', cond.type)
        self.body.validate(Context.new(None, ctx))
