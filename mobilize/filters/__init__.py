'''
Filters : functions that process and modify HTML snippets

A filter is a function designed to alter or process a block of
HTML-like code in some useful way.  It takes as input a string, meant
to be a snippet of HTML, and returns another string.  The returned
string may in general be the same thing as the input, but often it is
modified in some way.

FILTER API

A function conforms to the filter API if it:
  * accepts an lxml.html.HTMLElement instance as an argument, and
  * does not return any value,
  * operates by making any changes directly on the element as a side effect, and
  * is a no-op if the passed element is somehow not relevant to the particular filter (rather than raising an error).

'''

from .remove import (
    noinlinestyles,
    nomiscattrib,
    noevents,
    noimgsize,
    noattribs,
    omit,
    )

from .resize import (
    resizeobject,
    resizeiframe,
    )

from .tables import (
    table2divrows,
    table2divs,
    table2divgroups,
    )

COMMON_FILTERS = [
    noinlinestyles,
    noevents,
    nomiscattrib,
    ]

