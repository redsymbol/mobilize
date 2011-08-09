# Copyright 2010-2011 Mobile Web Up. All rights reserved.
def filterapi(filtfunc):
    '''
    Marks a callable as conforming to the filter API.
    '''
    filtfunc.is_filter = True
    return filtfunc

class Filter:
    '''
    Class-based filter
    '''
    is_filter = True

    def __call__(self, elem):
        assert False, 'subclass must implement'

    def relevant(self, reqinfo):
        '''
        Returns true iff this filter is relevant to the current page request

        This method can be used to conditionally apply a filter at the
        last possible moment, based on some aspect of the request.  It
        is used by handler.WebSourcer and subclasses, and may be used
        in other contexts as well,

        A good example use case is a filter you only want appled if
        the user-agent is, say, an iPhone, or Android device, etc.

        Filter subclasses may override this method.  If it returns
        True, the default, the filter is applied; on False, the
        filter is skipped.

        Note the filter-applying mechanism must support this relevance
        check.  All mechanisms in Mobilize are supposed to; if you
        find a place that it doesn't, that is a bug.  Any custom
        filter-applying mechanism (e.g., a Component that is not an
        Extracted subclass) will need to explictly invoke relevant()
        and handle it correctly.

        @param reqinfo : Request info (for the current request)
        @type  reqinfo : mobilize.httputil.RequestInfo

        @return        : True iff the component is relevant (and includable) for the current request
        @rtype         : str
        
        '''
        return True
