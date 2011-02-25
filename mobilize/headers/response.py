def location(environ, value):
    return value.replace(environ['MWU_OTHER_DOMAIN'], environ['HTTP_HOST'], 1)

def set_cookie(environ, value):
    return value

response_xforms = {
    'location'   : location,
    'set-cookie' : set_cookie,
    }
