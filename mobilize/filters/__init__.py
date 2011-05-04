'''
Filters: process and modify HTML snippets

A filter is a callable designed to alter or process a block of
HTML-like code in some useful way.  They operate on HtmlElement
instances, modifying them in place. The filtered element may in
general be the same as before, but often it is modified in some way.

FILTER API

A callable conforms to the filter API if it:
  * accepts an lxml.html.HTMLElement instance as an argument, and
  * does not return any value,
  * operates by making any changes directly on the element as a side effect, and
  * is a no-op if the passed element is somehow not relevant to the particular filter (rather than raising an error).

'''

from .remove import (
    nomiscattrib,
    noevents,
    noeventson,
    noimgsize,
    noattribs,
    omit,
    squeezebr,
    nobr,
    noinputwidth,
    )

from .resize import (
    resizeobject,
    resizeiframe,
    )

from .tables import (
    table2divrows,
    table2divs,
    table2divgroups,
    table2divgroupsgs,
    Spec,
    )

from .misc import (
    absimgsrc,
    abslinkfilesrc,
    )

DEFAULT_FILTERS = [
    noevents,
    nomiscattrib,
    ]
