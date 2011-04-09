'''
"todesktop" on-site desktop site selection

Herein lies code for an alternative mechanism for the visitor
registering their preference for the desktop view.  It is currently
not used; if we do use it, it will probably happen in the near future
(mid 2011).

If you see this in the far future (not mid 2011), then it is probably
cruft that can be deleted.  Note there is also a tests file,
test_todesktop.py.

To activate, place these lines toward the beginning of the wsgi
application function:

    if uri.startswith('/todesktop/'):
        return todesktop(environ, start_response, fullsite_domain)

'''
import re

_DEST_RE = re.compile(r'\bdest=([^&]+)')
def redir_dest(uri):
    '''
    Find the destination URI to redirect to on the desktop site

    Note that this takes in a relative URI, and returns a *different*
    relative URI.  The input URI is the link the person clicked on the
    mobile site, to switch to the desktop view.  The returned value is
    the URI they should be sent do on the desktop site.

    @param uri : URI of the redirecting GET request
    @type  uri : str

    @return    : destination URI on the desktop site
    @rtype     : str
    
    '''
    from urllib.parse import unquote
    match = _DEST_RE.search(uri)
    if match is not None:
        dest = unquote(match.group(1))
    else:
        dest = '/'
    return dest

def todesktop(environ, start_response, full_domain):
    '''
    Redirection to desktop view

    This WSGI sub-application will redirect the current page, assumed
    to be on the mobile view, to the corresponding page on the desktop
    view (site).
    '''
    uri = environ['REQUEST_URI']
    method = environ['REQUEST_METHOD'].upper()
    assert 'GET' == method, method
    dest = redir_dest(uri)
    assert dest.startswith('/'), dest
    headers = [
        ('Location', 'http://%s%s' % (full_domain, dest)),
        ('Set-Cookie', 'mredir=0; path=/'), # TODO: expires
        ]
    start_response('302 Found', headers)
    return ['']

