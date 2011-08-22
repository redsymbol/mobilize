# Copyright 2010-2011 Mobile Web Up. All rights reserved.
def location(environ, value):
    return value.replace(environ['MWU_OTHER_DOMAIN'], environ['HTTP_HOST'], 1)

import re
_set_cookie_re = re.compile(r'(?P<prefix>\bdomain\s*=\s*)(?P<domain>[^ ;]+)', re.I)
def _set_cookie_repl(match):
    domain = match.group('domain')
    pos = domain.find('.')
    if pos > 1 and (domain.count('.') == 2):
        domain = domain[pos:]
    return match.group('prefix') + domain

def set_cookie(environ, value):
    return _set_cookie_re.sub(_set_cookie_repl, value, count=1)

response_xforms = {
    'location'   : location,
    'set-cookie' : set_cookie,
    }
