# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Templating facilities
'''
import jinja2

def _mk_default_template_dirs():
    '''
    Calculate the default template directories from the mobile site
    Assumes a module "defs" is importable, which has a list
    TEMPLATE_DIRS.

    Note that the value of this will differ depending on the context
    in which it is imported, because it relies on a defs module that
    mobilize does not include (but the importing code is expected to
    have implemented).
    '''
    import os
    from mobilize import SITESKEL_ROOT
    try:
        from defs import TEMPLATE_DIRS as sitedirs
    except ImportError:
        sitedirs = []
    global_templates = [
        os.path.join(SITESKEL_ROOT, 'templates'),
        ]
    return sitedirs + global_templates

#: Default jinja2 template import directories
DEFAULT_TEMPLATE_DIRS = _mk_default_template_dirs()

class TemplateLoader:
    '''
    Loads a template
    '''
    def __init__(self, template_dirs = None):
        '''
        ctor

        Template_dirs defaults to DEFAULT_TEMPLATE_DIRS if not supplied.

        @param template_dirs : Paths of directories to search for template files
        @type  template_dirs : list of str
        
        '''
        if template_dirs is None:
            template_dirs = DEFAULT_TEMPLATE_DIRS
        assert len(template_dirs) > 0
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
    
