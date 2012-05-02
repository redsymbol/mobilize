# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Templating facilities
'''
import jinja2

class TemplateLoader:
    '''
    Loads a template
    '''
    def __init__(self, template_dirs = None):
        '''
        '''
        if template_dirs is None:
            template_dirs = default_template_dirs()
        self.template_dirs = template_dirs
        jloader = jinja2.FileSystemLoader(template_dirs)
        #cache = jinja2.MemcachedBytecodeCache('127.0.0.1:11211')
        self.jenv = jinja2.Environment(loader=jloader)

    def get_template(self, name):
        '''
        Load a template

        @param name : Name of template to load
        @type  name : str
        
        @return     : ready-to-render Jinja2 template
        @rtype      : jinja2.Template
        
        '''
        return self.jenv.get_template(name)
    
def default_template_dirs():
    '''
    Attempt to load the default template directories from the mobile site

    Assumes a module "defs" is importable, which has a list
    TEMPLATE_DIRS.

    If that is not the case, return an empty directory.
    '''
    start = [
        # HACK
        '/var/www/share/mobilize-libs/dev/siteskel/templates/',
        ]
    try:
        from defs import TEMPLATE_DIRS as sitedirs
    except ImportError:
        sitedirs = []
    return start + sitedirs

