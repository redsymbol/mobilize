def filterapi(filtfunc):
    '''
    Indicates a callable conforms to the filter API.
    '''
    filtfunc.is_filter = True
    return filtfunc
