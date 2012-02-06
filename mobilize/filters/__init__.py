# Copyright 2010-2012 Mobile Web Up. All rights reserved.
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

Callables that are filters are normally marked by the filters.filterbase.filterapi decorator.

'''

# TODO: automatically import all callables matching the filter api from the various submodules

from .filterbase import (
    filterapi,
    Filter,
    )

from .remove import (
    noattribs,
    nobr,
    noevents,
    noimgsize,
    noinputsize,
    nomiscattrib,
    nomiscattrib_if,
    omit,
    omitattrib_one,
    squeezebr,
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
    formaction,
    formcontroltypes,
    imgsub,
    relhyperlinks,
    relhyperlinks_full,
    )

DEFAULT_FILTERS = [
    nomiscattrib,
    ]
