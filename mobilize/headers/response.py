# Copyright 2010-2012 Mobile Web Up. All rights reserved.
def location(environ, value):
    return value.replace(environ['MWU_SRC_DOMAIN'], environ['HTTP_HOST'], 1)

import re
_set_cookie_re = re.compile(r'(?P<prefix>\bdomain\s*=\s*)(?P<domain>[^ ;]+)', re.I)
def _set_cookie_repl(match):
    domain = match.group('domain')
    if (not domain.startswith('.')) and domain.count('.') >= 2:
        parts = domain.split('.')
        domain = '.' + '.'.join(parts[-2:])
    return match.group('prefix') + domain

def set_cookie(environ, value):
    '''
    Modify the set-cookie value.

    Currently, all this does is check the Domain: morsel, if it
    exists.  If the value is specific to a subdomain
    (e.g. "Domain=foo.example.com"), rewrite it to be
    subdomain-agnostic ("Domain=.example.com").  This is so that
    cookies set on www.example.com will work correctly on
    m.example.com, etc.
    '''
    return _set_cookie_re.sub(_set_cookie_repl, value, count=1)

response_xforms = {
    'location'   : location,
    }
