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
    def __init__(self, rawstring):
        self.rawstring = rawstring

    def html(self):
        return self.rawstring
