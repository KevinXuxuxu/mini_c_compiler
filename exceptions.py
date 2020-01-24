class ParseException(Exception):
    pass

class UnexpectedEndOfTokenListException(ParseException):
    pass

class TokenizeFailedException(Exception):
    pass