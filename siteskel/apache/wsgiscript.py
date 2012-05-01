import os
import sys
from defs import (
    MOBILIZE_VERSION,
    MOBILE_DOMAIN,
    TEMPLATE_DIRS,
    )

sys.path.extend([
    '/var/www/%s/' % MOBILE_DOMAIN,
    '/var/www/%s/mobilize/' % MOBILE_DOMAIN,
    '/var/www/share/%s/' % MOBILE_DOMAIN,
    '/var/www/share/lib/',
    '/var/www/share/imgserve/',
    '/var/www/share/mobilize-libs/%s/' % MOBILIZE_VERSION,
    ])

from mobilize.httputil import mk_wsgi_application
from msite import msite
application = mk_wsgi_application(msite)
