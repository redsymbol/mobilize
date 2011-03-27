class MobilizeException(Exception):
    '''
    Base class of Mobilize-specific exceptions

    '''

class NoMatchingMoplateException(MobilizeException):
    '''
    Indicates no mobile template is available that matches the indicated URL
    '''

