class Component(object):
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
