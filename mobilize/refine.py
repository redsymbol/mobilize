'''
Selector Refinements

A REFINEMENT is a annotation or transformation of selector.  It can be
used to specify certain information or constraints about the selector,
as well as transform or generate content according to some algorithm.
'''
import types
import re

def mark_extracted(marker):
    def decfunc(f):
        def wrapped(*a, **kw):
            return f(*a, **kw)
        wrapped.extracted = marker
        return wrapped
    return decfunc

#: Marks a refinement as extracted from the full page's body
extracted = mark_extracted(True)

#: Marks a refinement as independent of the full page's body
unextracted = mark_extracted(False)

@unextracted
def raw_template(template_name, params=None):
    # load content from template
    if not params:
        params = {}
    from django.template.loader import render_to_string
    return render_to_string(template_name, params)

@unextracted
def raw_string(s):
    return s

@extracted
def xpath(selector):
    return selector
    
@extracted
def simple(selector):
    return simple2xpath(selector)

@extracted
def first(selector):
    # return first of 1 or more elements matching selector
    return nth(selector, 0)

@extracted
def nth(selector, n):
    assert False, 'not implemented yet'
    pass # Select the Nth item (zero based).  Indicates selector will generate N or more elements

_SELECTOR_SIMPLE = re.compile(r'(?P<tag>[a-zA-Z_-][a-zA-Z_0-9-]*)(?P<type>[#.])(?P<value>[a-zA-Z_-][a-zA-Z_0-9-]*)')
_SELECTOR_TYPETABLE = {
    '#' : 'id',
    '.' : 'class',
    }

def xpathsel(selector):
    '''
    Construct a full xpath expression from a selector

    A selector can be either a full xpath expression, or what's called
    a "simple selector".  A simple selector is in the format of
    "tagname#id" or "tagname.class", with a meaning much like in CSS.

    If the string is not recognized as a simple selector, it is
    assumed to be a valid xpath expression, and is returned unchanged.

    @param selector : Selector expression
    @type  selector : str
    
    @return         : xpath expression
    @rtype          : str
    
    '''
    xpath = selector
    match = _SELECTOR_SIMPLE.match(selector)
    if match:
        xpath = simple2xpath(selector, match)
    return xpath

def simple2xpath(selector, match = None):
    '''
    Create an xpath expression from a simple selector string

    The optional match argument is the result of matching to
    _SELECTOR_SIMPLE.  If not supplied, this function will calculate
    it.

    It is an error to invoke this on a selector that is not in the
    format of a "simple selector".

    @param selector : Simple selector
    @type  selector : str

    @param match    : (optional) Pre-matched regular expression
    @type  match    : RegexObject

    @return         : xpath expression
    @rtype          : str
    
    '''
    if not match:
        match = _SELECTOR_SIMPLE.match(selector)
    assert match, 'simple2xpath assumes the selector argument matches _SELECTOR_SIMPLE. Either "%s" does not, or a faulty match argument was supplied' % str(selector)
    params = {
        'tag' : match.group('tag'),
        'name' : _SELECTOR_TYPETABLE[match.group('type')],
        'value' : match.group('value'),
        }
    if 'class' == params['name']:
        # Since an HTML element may have 0 or more values for its class attribute, we need to handle it specially
        xpath = r'//%(tag)s[contains( normalize-space( @class ), " %(value)s " ) or substring( normalize-space( @class ), 1, string-length( "%(value)s" ) + 1 ) = "%(value)s " or substring( normalize-space( @class ), string-length( @class ) - string-length( "%(value)s" ) ) = " %(value)s" or @class = "%(value)s"]' % params
    else:
        xpath = r'//%(tag)s[@%(name)s="%(value)s"]' % params
    return xpath
