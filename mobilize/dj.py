# Copyright 2010-2011 Mobile Web Up. All rights reserved.
'''
Facilities making use of Django

'''

from .handlers import Moplate

def init_django(template_dirs):
    '''
    Initialize Django
    
    This must be called once per process, before any Django
    functionality (such as template rendering) is done.

    It cannot be invoked a second time, due to limitations in
    Django's settings/config system. As a consequence, it is not
    possible to change the init settings (such as template search
    dirs) without exiting and restarting the process.

    TODO: The above limitations can probably be worked around in the future

    @param template_dirs : Directories to search for templates
    @type  template_dirs : list of str

    '''
    from django.conf import settings
    try:
        settings.configure(TEMPLATE_DIRS=template_dirs)
    except RuntimeError:
        pass

class DjangoMoplate(Moplate):
    '''
    Represents a moplate rendered via the Django templating system

    Note that L{init_django} must be invoked before using most methods.

    '''

    def _render(self, params):
        '''
        TODO: assert that all expected template parameters are in fact
        present in the params dict.  Because of how django's template
        system currently works, may need to do this by a test render
        with dummy, sentinel-valued params, and scanning the output
        '''
        from django.template.loader import render_to_string
        return render_to_string(self.template_name, params)

