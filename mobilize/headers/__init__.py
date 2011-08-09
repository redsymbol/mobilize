# Copyright 2010-2011 Mobile Web Up. All rights reserved.
def _identity(environ, value):
    return value

def _get_xform_from(header, xforms):
    key = header.lower()
    if key in xforms:
        return xforms[key]
    return _identity

def get_request_xform(header, method='GET'):
    from .request import request_xforms
    return _get_xform_from(header, request_xforms)

def get_response_xform(header, method='GET'):
    from .response import response_xforms
    return _get_xform_from(header, response_xforms)
