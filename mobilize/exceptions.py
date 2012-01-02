# Copyright 2010-2012 Mobile Web Up. All rights reserved.
class MobilizeException(Exception):
    '''
    Base class of Mobilize-specific exceptions

    '''

class NoMatchingHandlerException(MobilizeException):
    '''
    Indicates no handler is available that matches the given URL/dispatch
    '''

