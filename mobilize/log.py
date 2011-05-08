'''
Mobilize logging facilities

'''

def mk_wsgi_log(environ):
    '''
    Create a webserver logging function for a wsgi environment

    This will return a callable that writes to the wsgi.errors file,
    which normally means that messages will be written in the web
    server error log for this (virtual)host.

    Tne callable takes a single argument, a string, which is written
    to the web server error log:

      log = mk_wsgi_log(wsgienviron)
      log('Hello World')

    @param environ : WSGI environment
    @type  environ : dict
    
    '''
    logger = Logger(environ['wsgi.errors'])
    return logger.log
    
class Logger:
    '''
    Class for logging
    '''

    def __init__(self, outf):
        '''
        ctor

        @param outf : File to write log messages to
        @type  outf : quacks like a file
        
        '''
        self.outf = outf

    def log(self, msg):
        '''
        Write a message
        '''
        if not msg.endswith('\n'):
            msg += '\n'
        self.outf.write(msg)
