# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Utilities for individual mobilize sites
'''
def mk_tparams(sitedefs, is_https=False):
    '''
    Create the tparams function

    Each mobile site has a tparams function used to create the
    template parameters for a particular mobile page view. The
    function takes 0 or more key-value pair arguments, and returns a
    dictionary which is intended to be passed to the template
    renderer.

    Normally a mobile site will have a single tparams function that is
    used by all moplates and mobile views.  When called with no
    arguments, tparams() will return a default parameter set.  When
    called with key-value pairs, the dictionary will be updated with
    them: in other words, the following two are equivalent:

      p = tparams(**kw)
      p = tparams(); p.update(kw)

    @param sitedefs : Mobile site defs module
    @type  sitedefs : module

    @param is_https : Whether the site is https
    @type  is_https : bool

    @return         : tparams callable
    @rtype          : function
    
    '''
    if is_https:
        globalstatic_url = 'https://gs-mobilewebup-com.s3.amazonaws.com/'
    else:
        globalstatic_url = 'http://gs.mobilewebup.com/'
    
    default_params = {
        'default_title'    : getattr(sitedefs, 'DEFAULT_TITLE', ''),
        'http_domain'      : sitedefs.HTTP_MOBILE_DOMAIN,
        'fullsite'         : sitedefs.DESKTOP_DOMAIN,
        'static_url'       : '/_mwu/',
        'globalstatic_url' : globalstatic_url,
        }
    
    def tparams(**kw):
        '''
        Parameters for templates.  Common defaults, overrideable with keyword parameters.
        '''
        p = dict(default_params)
        p.update(kw)
        return p
    return tparams
