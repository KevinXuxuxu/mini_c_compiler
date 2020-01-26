from tree import *
from exceptions import *
from collections import namedtuple, defaultdict
from random import randint

class Context(namedtuple('Context', ['id', 'type'])):

    def __repr__(self):
        return "C({}, {})".format(self.id, self.type)

class Validator:

    current_ctx = 0

    def new_ctx(self, _type=None):
        self.current_ctx += 1
        return Context(self.current_ctx, _type)

    def get_max_ctx_before(self, ctx_map, ctx):
        maxi = Context(-1, None)
        for x in ctx_map:
            if x.id < ctx.id and x.id > maxi.id:
                maxi = x
        return ctx_map[maxi]

    def get_type(self, name, _map, ctx):
        if name in _map:
            if ctx in _map[name]:
                return _map[name][ctx]
            return self.get_max_ctx_before(_map[name], ctx)
        raise UndefinedException(None, name)

    def get_var_type(self, name, v_map, ctx):
        try:
            return self.get_type(name, v_map, ctx)
        except UndefinedException as e:
            raise UndefinedVariableException(e.name)

    def get_func_type(self, name, f_map, ctx):
        try:
            return self.get_type(name, f_map, ctx)
        except UndefinedException as e:
            raise UndefinedFunctionException(e.name)

    def validate(
        self,
        node,
        v_map=defaultdict(dict),
        f_map=defaultdict(dict),
        ctx=Context(0, None)
    ):
        # print("v_map: {}".format(v_map))
        # print("f_map: {}".format(f_map))
        # print("context: {}".format(ctx))
        # print("what: {}".format(node))
        # print()
        if isinstance(node, Root):
            for f in node.functions:
                self.validate_func_def(f, v_map, f_map, ctx)
        elif isinstance(node, VarDef):
            self.validate_var_def(node, v_map, f_map, ctx)
        elif isinstance(node, Block):
            for st in node.statements:
                self.validate(st, v_map, f_map, ctx)
        elif isinstance(node, FuncDef):
            self.validate_func_def(node, v_map, f_map, ctx)
        elif isinstance(node, UnaryOp):
            # TODO: implement implicit type cast
            self.validate(node.child, v_map, f_map, ctx)
            node.check_type()
        elif isinstance(node, BinaryOp):
            # TODO: implement implicit type cast
            self.validate(node.left, v_map, f_map, ctx)
            self.validate(node.right, v_map, f_map, ctx)
            node.check_type()
        elif isinstance(node, FuncCall):
            node.type, v_types = self.get_func_type(node.name, f_map, ctx)
            params = node.params
            if len(params) != len(v_types):
                raise WrongNumberOfArguments(node.name, len(v_types), len(params))
            for i, expr in enumerate(params):
                self.validate(expr, v_map, f_map, ctx)
                if v_types[i] != expr.type:
                    raise TypeMismatchException(v_types[i], expr.type)
        elif isinstance(node, VarRef):
            node.type = self.get_var_type(node.name, v_map, ctx)
        elif isinstance(node, Block):
            for statement in node.statements:
                self.validate(statement, v_map, f_map, ctx)
        elif isinstance(node, Assignment):
            self.validate(node.var_ref, v_map, f_map, ctx)
            self.validate(node.expr, v_map, f_map, ctx)
            BinaryOp(node.op[0], node.expr, node.var_ref).check_type()
        elif isinstance(node, Return):
            if ctx.type is None:
                raise BadReturnException()
            if node.expr == None:
                if ctx.type != 'void':
                    raise TypeMismatchException(ctx.type, 'void')
            else:
                self.validate(node.expr, v_map, f_map, ctx)
                if ctx.type != node.expr.type:
                    raise TypeMismatchException(ctx.type, node.expr.type)

                
    def validate_func_def(self, node, v_map, f_map, ctx):
        name, _type = node.name, node.type
        if name in f_map and ctx in f_map[name]:
            # TODO: support function overloading
            raise FunctionDefDuplication(
                "Function {} already defined in this context".format(name))
        new_v_map, new_f_map, new_ctx = v_map.copy(), f_map.copy(), self.new_ctx(_type)
        for v in node.args:
            has_default = self.validate_var_def(v, new_v_map, new_f_map, new_ctx)
            if has_default:
                raise DefaultParameterInFunctionDef(name, v.name)
        f_map[name][ctx] = (_type, [v.type for v in node.args])
        self.validate(node.body, new_v_map, new_f_map, new_ctx)

    def validate_var_def(self, node, v_map, f_map, ctx):
        name, _type, default = node.name, node.type, node.default
        self.validate(default, v_map, f_map, ctx)
        if name in v_map and ctx in v_map[name]:
            raise VariableDefDuplication(
                "Variable {} already defined in this context".format(name))
        if default != None:
            if default.type != _type:
                raise TypeMismatchException(_type, default.type)
        v_map[name][ctx] = _type
        return default != None
        