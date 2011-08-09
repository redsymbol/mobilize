# Copyright 2010-2011 Mobile Web Up. All rights reserved.
def filterapi(filtfunc):
    '''
    Indicates a callable conforms to the filter API.
    '''
    filtfunc.is_filter = True
    return filtfunc
