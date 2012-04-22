# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Mobilize logging facilities

'''

import logging
logging.basicConfig(level=logging.DEBUG)

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
