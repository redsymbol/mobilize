# TODO: use abc

from mobilize import common
from common import Component

class Unextracted(Component):
    '''abstract base of all components that are independent of the source HTML page'''
    extracted = False

class DjangoTemplate(Unextracted):
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

class RawString(Unextracted):
    def __init__(self, rawstring):
        self.rawstring = rawstring

    def html(self):
        return self.rawstring
