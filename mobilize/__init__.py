# Copyright 2010-2011 Mobile Web Up. All rights reserved.
'''
Mobilize - the Mobile Web Up platform

B{Mobilize} is a framework for the automated creation of mobile
websites from desktop-oriented, "full" sites.  It allows realtime
synchronization regardless of the full site's underlying platform;
device-specific adaptation; and many other flexible, powerful,
extensible features.

'''
from .base import *
from .dj import DjangoMoplate
from .handlers import (
    todesktop,
    passthrough,
    )

__all__ = [
    'MobileSite',
    'DjangoMoplate',
    ]
