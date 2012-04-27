# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Utilities used by tests in this project
'''

import os
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_TEMPLATE_DIR = os.path.join(TEST_DATA_DIR, 'templates')

def data_file_path(*components):
    '''
    path to test data file
    '''
    parts = [os.path.dirname(__file__), 'data'] + list(components)
    return os.path.join(*parts)

def normxml(s):
    '''
    normalize an XML string for relaxed comparison
    '''
    if type(s) is bytes:
        s = s.decode()
    from lxml import html
    unstripped = html.tostring(html.fromstring(str(s)), pretty_print=True).decode('utf-8')
    return ''.join(line.strip() for line in unstripped.split('\n'))

def gtt(name):
    '''
    Get Test Template - load a test template

    @param name : name of template to load
    @type  name : str

    @return     : template object
    @rtype      : jinja2.Template
    
    '''
    from mobilize.templates import TemplateLoader
    loader = TemplateLoader([TEST_TEMPLATE_DIR])
    return loader.get_template(name)
