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

class FuncDef(namedtuple('FuncDef', ['name', 'type', 'args', 'body']), Tree):
    pass

class Literal(namedtuple('Literal', ['type', 'value']), Tree):
    pass

class VarDef(namedtuple('VarDef', ['name', 'type', 'default']), Tree):
    pass

class UnaryOp(namedtuple('UnaryOp', ['op', 'child']), Tree):
    pass

class BinaryOp(namedtuple('BinaryOp', ['op', 'right', 'left']), Tree):
    pass

class FuncCall(namedtuple('FuncCall', ['name', 'params']), Tree):
    pass

class Param(namedtuple('Param', ['name', 'expr']), Tree):
    pass

class Block(namedtuple('Block', ['statements']), Tree):
    pass

class Assignment(namedtuple('Assignment', ['name', 'op', 'expr']), Tree):
    pass
