def host(environ, value):
    return environ['MWU_OTHER_DOMAIN']

def cookie(environ, value):
    return value

request_xforms = {
    'host'   : host,
    'cookie' : cookie,
    }

