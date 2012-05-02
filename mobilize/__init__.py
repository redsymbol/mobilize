# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Mobilize - the Mobile Web Up platform

B{Mobilize} is a framework for the automated creation of mobile
websites from desktop-oriented, "full" sites.  It allows realtime
synchronization regardless of the full site's underlying platform;
device-specific adaptation; and many other flexible, powerful,
extensible features.

'''
import os

from .base import *
from .handlers import (
    todesktop,
    passthrough,
    Moplate,
    )

MOBILIZE_ROOT = os.path.dirname(__file__)
SITESKEL_ROOT = os.path.join(MOBILIZE_ROOT, '..', 'siteskel')

__all__ = [
    'MobileSite',
    'Moplate',
    'Domains',
    ]
