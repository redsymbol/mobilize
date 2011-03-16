def host(environ, value):
    return environ['MWU_OTHER_DOMAIN']

def cookie(environ, value):
    return value

def referer(environ, value):
    return value.replace(environ['HTTP_HOST'], environ['MWU_OTHER_DOMAIN'], 1)

request_xforms = {
    'host'   : host,
    'cookie' : cookie,
    'referer' : referer,
    }

