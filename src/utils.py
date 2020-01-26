cache = {
        '\'':"\\'",
        '\"':'\\"',
        '\a':'\\a',
        '\b':'\\b',
        '\f':'\\f',
        '\n':'\\n',
        '\r':'\\r',
        '\t':'\\t',
        '\v':'\\v'
    }

def unescape(x):
    if not isinstance(x, str):
        return x
    y = x
    for k, v in cache.items():
        y = y.replace(k, v)
    return "'{}'".format(y)