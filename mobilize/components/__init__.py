'''
Mobilize page components

Components are pieces of web content assembled within a moplate to
form the final mobile web page.  You can usually think of them as just
HTML fragments.  More accurately, a component is an object that knows
how to generate and render an HTML fragment.  During page rendering, a
the fragments form a sequence of these components are strung together
in order.  This forms the core content of the mobile page (normally
laid out in a single vertical column).

There are two broad types of components: *simple* and *extracted*.
The main difference is that extracted components create their content
using the desktop page as a source.  They will take a portion of the
source page HTML, modifying it in some way to form a piece of the
mobile page.  In contrast, the HTML content of simple components can
be created in a variety of ways - some potentially complex, despite
the name - but never by parsing the desktop page content.

'''

from simple import *
from extracted import *
