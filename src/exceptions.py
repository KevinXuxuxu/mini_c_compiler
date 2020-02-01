class ParseException(Exception):
    pass

class UnexpectedEndOfTokenListException(ParseException):
    pass

class ExpressionParseException(ParseException):
    pass

class TokenizeFailedException(Exception):
    pass

class ValidationException(Exception):
    pass

class DefinitionDuplicationException(ValidationException):

    def __init__(self, what, name):
        super().__init__("{} {} is already defined in this context".format(what, name))

class FunctionDefDuplication(DefinitionDuplicationException):
    
    def __init__(self, name):
        super().__init__('Function', name)

class VariableDefDuplication(DefinitionDuplicationException):
    
    def __init__(self, name):
        super().__init__('Variable', name)

class TypeMismatchException(ValidationException):
    
    def __init__(self, expected, got):
        super().__init__("Expecting {} but got {}".format(expected, got))

class UndefinedException(ValidationException):

    def __init__(self, what, name):
        super().__init__(
            "{} '{}' is not defined in this context".format(what, name))
        self.name = name

class UndefinedVariableException(UndefinedException):

    def __init__(self, name):
        super().__init__('Variable', name)

class UndefinedFunctionException(UndefinedException):

    def __init__(self, name):
        super().__init__('Function', name)

class DefaultParameterInFunctionDef(ValidationException):

    def __init__(self, f_name, v_name):
        super().__init__("""Parameter with default value is not supported in C.
        Parameter '{}' in function '{}'
        """.format(v_name, f_name))

class WrongNumberOfArguments(ValidationException):

    def __init__(self, name, expected, got):
        super().__init__("""Wrong number of argument for function call {}
        Expected {} but got {}
        """.format(name, expected, got))

class UnexpectedReturnException(ValidationException):
    pass

class UnreturnedFunctionException(ValidationException):

    def __init__(self, name):
        super().__init__("Function {} is not returned".format(name))

class ArrayTypeException(ValidationException):

    def __init__(self, name):
        super().__init__("Definition of variable {} with array type needs \
            an explicit size or an initializer".format(name))

class ArrayInitializeException(ValidationException):

    def __init__(self, name, expected, got):
        super().__init__("Expecting {} elements in initializing array {} but got {}".format(
            expected, name, got))
