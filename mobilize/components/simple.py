# Copyright 2010-2011 Mobile Web Up. All rights reserved.
# TODO: use abc

from mobilize import util
from .common import Component

class Simple(Component):
    '''abstract base of all components that are independent of the source HTML page'''
    extracted = False

class DjangoTemplate(Simple):
    '''
    Render directly from a django template
    '''
    def __init__(self, template, params = None):
        '''
        @param template : Path to the django template to render
        @type  template : str

        @param params   : Template parameters
        @type  params   : dict
        
        '''
        if not params:
            params = {}
        self.template = template
        self.params = params

    def html(self):
        from django.template.loader import render_to_string
        return render_to_string(self.template, self.params)

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
        super(Clear, self).__init__('<div style="clear: both;">&nbsp;</div>\n')
