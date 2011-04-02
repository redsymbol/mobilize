class RefineClassBase(object):
    '''abstract base of all refinement classes'''
    def html(self):
        '''
        Render the element content HTML

        @return : html snippet/content
        @rtype  : str
        
        '''
        assert False, 'Subclass must implement'
