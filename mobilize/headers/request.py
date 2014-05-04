def host(environ, value):
    return environ['MWU_SRC_DOMAIN']

def source_referer(environ, value):
    return value.replace(environ['HTTP_HOST'], environ['MWU_SRC_DOMAIN'], 1)

# Standard transformations of existing request headers
request_xforms = {
    'host'   : host,
    }

# Standard additions to request headers
request_additions = [
    # When you re-enable X-MWU-Mobilize, be sure to also activate test_get_request_headers in test_httputils.py
    ('X-MWU-Mobilize', lambda e, v: '1' ),
    ('X-Forwarded-For',  lambda e, v: e['REMOTE_ADDR']),
    ]
