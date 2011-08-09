class Component:
    '''
    abstract base of all component classes

    '''
    def html(self):
        '''
        Render the element content HTML

        TODO: use abc (abstract base classes)

        @return : html snippet/content
        @rtype  : str
        
        '''
        assert False, 'Subclass must implement'

    def relevant(self, reqinfo):
        '''
        Returns true iff this component is relevant to the current page request

        This method can be used to conditionally include or omit
        components at the last possible moment, based on some aspect
        of the request.  It is used by handler.WebSourcer and
        subclasses, and may be used in other contexts as well,

        A good example use case is a component that you only want to
        include if the user-agent is, say, an iPhone, or Android
        device, etc.

        Component subclasses may override this method.  If it returns
        True, the default, the component is included; on False, the
        component is left out of the rendering.

        @param reqinfo : Request info (for the current request)
        @type  reqinfo : mobilize.httputil.RequestInfo

        @return        : True iff the component is relevant (and includable) for the current request
        @rtype         : str
        
        '''
        return True
