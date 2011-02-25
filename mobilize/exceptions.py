class MobilizeException(Exception):
    '''
    Base class of Mobilize-specific exceptions

    '''

class NoMatchingTemplateException(MobilizeException):
    '''
    Indicates no mobile template is available that matches the indicated URL
    '''

