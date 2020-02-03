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


class Mem:

    def __init__(self, _type, value):
        self.type = _type
        if isinstance(value, list):
            self.len = len(value)
        else:
            self.len = None
        self.value = value

    def __repr__(self):
        return "M({}, {}, {})".format(self.type, self.len, self.value)

    def check_type(self, v):
        _type, _len = self.type, self.len
        if _len == None or (not isinstance(v, list)):
            if _type in ['int', 'bool']:
                if _type != type(v).__name__:
                    raise RuntimeError("Type mismatch, expecting {} but got {}".format(
                        _type, type(v).__name__))
            elif _type == 'char':
                if type(v).__name__ != 'str' or len(v) != 1:
                    raise RuntimeError("Type mismatch, expecting {} but got {}".format(
                        _type, type(v).__name__))
            else:
                raise RuntimeError("Unexpected type {}".format(_type))
        else:
            if _type in ['int', 'bool']:
                if any(_type != type(i).__name__ for i in v):
                    raise RuntimeError("Type mismatch, expecting {} but got {}".format(
                        _type, v))
            elif _type == 'char':
                if any(type(i).__name__ != 'str' or len(i) != 1 for i in v):
                    raise RuntimeError("Type mismatch, expecting {} but got {}".format(
                        _type, v))
            else:
                raise RuntimeError("Unexpected type {}".format(_type))

    def put(self, v, i=None):
        self.check_type(v)
        if i is None:
            self.value = v
        else:
            self.value[i] = v

    def get(self, i=None):
        if i is None:
            return self.value
        return self.value[i]

class ReturnValue:

    def __init__(self, v):
        self.v = v

class Context(namedtuple('Context', ['id', 'type', 'parent', 'v_map', 'f_map'])):
    returned = False
    
    def __repr__(self):
        return "C({}, {} , {}, {}, {})".format(
            self.id,
            self.type,
            self.parent.id if self.parent else "None",
            self.v_map,
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
    def new(cls, _type, parent, name=""):
        _id = "{}_{}".format(name, randint(1, 10000))
        return Context(_id, _type, parent, {}, {})


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

    def evaluate(self, ctx):
        raise RuntimeError("Unimplemented evaluation function on {}".format(self))

class Typable(Tree):
    type = None
    extra_fields = ['type']

class Expr(Tree):
    pass

class Root(namedtuple('Root', ['functions']), Tree):
    
    def validate(self, ctx=Context(0, None, None, {}, {})):
        for f in self.functions:
            f.validate(ctx)

    def evaluate(self, ctx=Context(0, None, None, {}, {})):
        for f in self.functions:
            if f.name == 'main':
                return f.evaluate(ctx)
            f.register(ctx)

class FuncDef(namedtuple('FuncDef', ['type', 'name', 'args', 'body']), Tree):
    
    def validate(self, ctx):
        name, _type = self.name, self.type
        if name in ctx.f_map:
            raise FunctionDefDuplication(name)
        ctx.f_map[name] = (_type, [v.type for v in self.args])
        new_ctx = Context.new(_type, ctx, name)
        if name == 'main' and len(self.args) != 0:
            raise WrongNumberOfArguments(name, 0, len(self.args))
        for v in self.args:
            has_default = v.validate(new_ctx)
            if has_default:
                raise DefaultParameterInFunctionDef(name, v.name)
        self.body.validate(new_ctx)
        if _type != 'void' and not new_ctx.returned:
            raise UnreturnedFunctionException(name)

    def register(self, ctx):
        ctx.f_map[self.name] = self

    def evaluate(self, ctx, params=[]):
        new_ctx = Context.new(self.type, ctx, self.name)
        assert len(params) == len(self.args)
        for i, arg in enumerate(self.args):
            arg.evaluate(new_ctx)
            var_ref = VarRef(arg.name)
            a = Assignment(var_ref, '=', params[i])
            a.evaluate(new_ctx)
        return self.body.evaluate(new_ctx).v

class Literal(namedtuple('Literal', ['type', 'value']), Expr):

    def evaluate(self, ctx):
        return self.value

class ArrayInit(namedtuple('ArrayInit', ['len', 'value']), Typable):

    def validate(self, ctx):
        for i in self.len:
            self.value[i].validate(ctx)
        _type= self.value[0].type
        if not all(v.type == _type for v in self.value):
            raise ValidationException("Values of different types are in the same array")
        self.type = self.value[0].type

    def evaluate(self, ctx):
        return [v.evaluate(ctx) for v in self.value]

class VarDef(namedtuple('VarDef', ['name', 'type', 'default']), Tree):

    extra_fields = ['len']

    nil = {
        'int': 0,
        'bool': False,
        'chr': ' ',
    }

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
    
    def evaluate(self, ctx):
        default_value = None
        if self.default != None:
            default_value = self.default.evaluate(ctx)
        else:
            if self.len == None:
                default_value = self.nil[self.type]
            else:
                default_value = [self.nil[self.type] for i in range(self.len)]
        ctx.v_map[self.name] = Mem(self.type, default_value)

class Operator(Typable, Expr):
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
        if not isinstance(self.child, Reference):
            raise ValidationException(
                "Expecting a reference with {} operator".format(self.op))
        c_type, allowed = self.child.type, self.type_map[self.op]
        if c_type not in allowed:
            return TypeMismatchException(allowed, c_type)
        self.type = c_type
    
    def validate(self, ctx):
        self.child.validate(ctx)
        self.check_type()

    def evaluate(self, ctx):
        child, op = self.child, self.op
        v = child.evaluate(ctx)
        if op in '+-':
            return eval(op + str(v))
        if op[0] in 'RL':
            mem = ctx.get_var(child.name)
            new_v = eval("{}{}1".format(v, op[1]))
            if isinstance(child, VarRef):
                mem.put(new_v)
            elif isinstance(child, ArrayRef):
                i = child.index.evaluate(ctx)
                mem.put(new_v, i)
            else:
                raise RuntimeError("Unexpected operand for {}: {}".format(op, child))
            return new_v if op[0] == 'L' else v
        if op == '!':
            return eval("not {}".format(v))
        if op == '~':
            C = 2147483648
            return -(((v + C) % (2*C) - C) + 1)

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

    def evaluate(self, ctx):
        op, left, right = self.op, self.left.evaluate(ctx), self.right.evaluate(ctx)
        if op in '+-*/%><' or op in ['>=', '<=', '==', '!=']:
            if op == '/':
                op = '//'
            return eval("{}{}{}".format(left, op, right))
        if op == '&&':
            return eval("{} and {}".format(left, right))
        if op == '||':
            return eval("{} or {}".format(left, right))
        raise RuntimeError("Operator {} not supported yet".format(op))

class FuncCall(namedtuple('FuncCall', ['name', 'params']), Typable, Expr):
    
    def validate(self, ctx):
        self.type, v_types = ctx.get_func(self.name)
        params = self.params
        if len(params) != len(v_types):
            raise WrongNumberOfArguments(self.name, len(v_types), len(params))
        for i, expr in enumerate(params):
            expr.validate(ctx)
            if v_types[i] != expr.type:
                raise TypeMismatchException(v_types[i], expr.type)

    def evaluate(self, ctx):
        func = ctx.get_func(self.name)
        param_values = [p.evaluate(ctx) for p in self.params]
        return func.evaluate(ctx, param_values)

class Reference(Typable, Expr):
    pass

class VarRef(namedtuple('VarRef', ['name']), Reference):

    def validate(self, ctx):
        self.type, _ = ctx.get_var(self.name)

    def evaluate(self, ctx):
        return ctx.get_var(self.name).get()

class ArrayRef(namedtuple('ArrayRef', ['name', 'index']), Reference):

    def validate(self, ctx):
        self.type, is_array = ctx.get_var(self.name)
        if not is_array:
            raise NotAnArrayException(self.name)
        self.index.validate(ctx)
        if self.index.type != 'int':
            raise TypeMismatchException('int', self.index.type)

    def evaluate(self, ctx):
        i = self.index.evaluate(ctx)
        return ctx.get_var(self.name).get(i)

# class Param(namedtuple('Param', ['name', 'expr']), Tree):
#     pass

class Block(namedtuple('Block', ['statements']), Tree):

    def validate(self, ctx):
        for st in self.statements:
            st.validate(ctx)

    def evaluate(self, ctx):
        for st in self.statements:
            v = st.evaluate(ctx)
            if isinstance(v, ReturnValue):
                return v
        return None

class Assignment(namedtuple('Assignment', ['ref', 'op', 'expr']), Tree):

    def validate(self, ctx):
        self.ref.validate(ctx)
        self.expr.validate(ctx)
        BinaryOp(self.op[0], self.expr, self.ref).check_type()

    def evaluate(self, ctx):
        ref, op, expr = self.ref, self.op, self.expr
        if isinstance(expr, Expr):
            expr = expr.evaluate(ctx)
        mem = ctx.get_var(ref.name)
        if isinstance(ref, VarRef):
            if op == '=':
                mem.put(expr)
            else:
                original_value = mem.get()
                code = "{}{}{}".format(original_value, op[0], expr)
                mem.put(eval(code))
        else:
            i = ref.index.evaluate(ctx)
            if op == '=':
                mem.put(expr, i)
            else:
                original_value = mem.get(i)
                code = "{}{}{}".format(original_value, op[0], expr)
                mem.put(eval(code), i)

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

    def evaluate(self, ctx):
        return ReturnValue(self.expr.evaluate(ctx))

class If(namedtuple('If', ['cond', 'true_body', 'false_body']), Tree):
    
    def validate(self, ctx):
        cond = self.cond
        cond.validate(ctx)
        if cond.type != 'bool':
            raise TypeMismatchException('bool', cond.type)
        self.true_body.validate(Context.new(None, ctx))
        if self.false_body != None:
            self.false_body.validate(Context.new(None, ctx))

    def evaluate(self, ctx):
        if self.cond.evaluate(ctx):
            return self.true_body.evaluate(Context.new(None, ctx))
        if self.false_body != None:
            return self.false_body.evaluate(Context.new(None, ctx))

class While(namedtuple('While', ['cond', 'body']), Tree):
    
    def validate(self, ctx):
        cond = self.cond
        cond.validate(ctx)
        if cond.type != 'bool':
            raise TypeMismatchException('bool', cond.type)
        self.body.validate(Context.new(None, ctx))
