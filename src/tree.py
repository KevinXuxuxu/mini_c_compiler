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
from utils import unescape
from exceptions import *

class Tree:
    """ This is an interface"""
    unit = ' '*3
    
    def to_str(self, i=1):
        s = "{}:\n".format(type(self).__name__)
        for field in self._fields:
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


class Root(namedtuple('Root', ['functions']), Tree):
    pass

class FuncDef(namedtuple('FuncDef', ['type', 'name', 'args', 'body']), Tree):
    pass

class Literal(namedtuple('Literal', ['type', 'value']), Tree):
    pass

class Typable(Tree):
    type = None

class VarDef(namedtuple('VarDef', ['name', 'type', 'default']), Tree):
    pass

class VarRef(namedtuple('VarRef', ['name']), Typable):
    pass

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
    
    def check_type(self):
        l_type, r_type, allowed = self.left.type, self.right.type, self.type_map[self.op]
        if allowed != '*' and l_type not in allowed:
            raise TypeMismatchException(allowed, l_type)
        if r_type != l_type:
            raise TypeMismatchException(l_type, r_type)
        self.type = l_type

class FuncCall(namedtuple('FuncCall', ['name', 'params']), Typable):
    pass

# class Param(namedtuple('Param', ['name', 'expr']), Tree):
#     pass

class Block(namedtuple('Block', ['statements']), Tree):
    pass

class Assignment(namedtuple('Assignment', ['var_ref', 'op', 'expr']), Tree):
    pass

class Return(namedtuple('Return', ['expr']), Tree):
    pass
