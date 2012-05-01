# Copyright 2010-2012 Mobile Web Up. All rights reserved.
# TODO: use abc

from mobilize import util
from .common import Component

class Simple(Component):
    '''abstract base of all components that are independent of the source HTML page'''
    extracted = False

class FromTemplate(Simple):
    '''
    Render directly from a jinja2 template
    '''
    def __init__(self, template_name, params = None, template_dirs=None):
        '''
        @param template : Path to the jinja2 template file to render
        @type  template : str

        @param params   : Template parameters
        @type  params   : dict
        
        '''
        if not template_dirs:
            from mobilize.templates import default_template_dirs
            self.template_dirs = default_template_dirs()
        else:
            self.template_dirs = template_dirs
        if not params:
            params = {}
        self.template_name = template_name
        self.params = params

    def html(self):
        from mobilize.templates import TemplateLoader
        loader = TemplateLoader(self.template_dirs)
        return loader.get_template(self.template_name).render(**self.params)

class RawString(Simple):
    '''
    Insert a string directly into the mobile component stream
    '''
    def __init__(self, rawstring):
        self.rawstring = rawstring

    def html(self):
        return self.rawstring

class Clear(RawString):
    '''
    Insert a clearfix element

    This implements a clearfix by inserting an element the horribly
    nonsemantic, but widely supported way.

    At some point, hopefully we'll come up with a solely CSS clearfix
    that works across all mobile browsers, obsoleting this component
    entirely.

    '''
    def __init__(self):
        super().__init__('<div style="clear: both;">&nbsp;</div>\n')
