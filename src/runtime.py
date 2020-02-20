import re
import utils

from tree import Tree
from collections import namedtuple
from exceptions import *

# statement but not expression
class Runtime(Tree):

    @classmethod
    def parse(cls, name, params):
        if name == 'printf':
            return Printf(params[0], params[1:])
        raise UnimplementedRuntimeException(name)

class Printf(namedtuple('Printf', ['format', 'params']), Runtime):

    type_map = {
        '%i': 'int',
        '%d': 'int',
        '%c': 'char',
        '%s': 'string'
    }
    
    def validate(self, ctx):
        self.format.validate(ctx)
        for p in self.params:
            p.validate(ctx)
        utils.check_type('string', self.format.type)
        # TODO: move type check for value render to here instead of throw runtime error

    def evaluate(self, ctx):
        # only support %d, %i for integer, %c for character and %s for string
        _format = self.format.evaluate(ctx)
        holes = re.findall(r'%[dics]', _format)
        params = self.params
        if len(holes) != len(params):
            raise WrongNumberOfArguments('printf', len(holes) + 1, len(params) + 1)
        for i in range(len(holes)):
            utils.check_type(self.type_map[holes[i]], params[i].type)
        values = [p.evaluate(ctx) for p in params]
        print(_format % tuple(values), end='')
        return None
