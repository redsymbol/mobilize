# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Mobilize logging facilities

'''

import logging

def wsgilog(environ):
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
    return Logger()
    
class Logger:
    '''
    Class for logging
    '''

    def __init__(self):
        '''
        ctor

        '''
        logging.critical('Starting new-style logger')

    def msg(self, msg):
        '''
        Write a message
        '''
        logging.warn(msg)

    def headers(self, label, reqinfo, headers, **kw):
        '''
        Log http headers
        '''
        msg = '%s (%s %s): %s' % (
            label,
            reqinfo.method,
            reqinfo.uri,
            str(headers),
            )
        for k, v in kw.items():
            msg += ', %s=%s' % (k, v)
        self.msg(msg)
