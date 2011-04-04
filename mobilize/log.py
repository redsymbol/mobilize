'''
Mobilize logging facilities

'''

class WsgiLogger(object):
    '''
    Class for logging to WSGI web server
    '''

    def __init__(self, outf):
        '''
        ctor

        @param outf : File to write log messages to
        @type  outf : quacks like a file
        
        '''
        self.outf = outf

    @classmethod
    def create(Cls, environ):
        '''
        Create a logger for a wsgi environment

        This will return a logger that writes to the wsgi.errors file,
        which normally means that messages will be written in the web
        server error log for this (virtual)host.

        @param environ : WSGI environment
        @type  environ : dict
        
        '''
        logger = Cls(environ['wsgi.errors'])
        return logger

    def log(self, msg):
        '''
        Write a message
        '''
        if not msg.endswith('\n'):
            msg += '\n'
        self.outf.write(msg)
