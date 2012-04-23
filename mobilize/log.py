# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Mobilize logging facilities

'''

import logging

# The mobile site can set LOGLEVEL in defs.py
try:
    from defs import LOGLEVEL
except ImportError:
    LOGLEVEL = logging.WARNING
logging.basicConfig(level=LOGLEVEL)

def format_headers_log(label, reqinfo, headers, **kw):
    '''
    Format HTTP headers for logging
    '''
    msg = '%s (%s %s): %s' % (
        label,
        reqinfo.method,
        reqinfo.uri,
        str(headers),
        )
    for k, v in kw.items():
        msg += ', %s=%s' % (k, v)
    return msg
