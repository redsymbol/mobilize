'''
Security protections

This module provides tools for preventing the exploit of security
holes in the source, desktop website.  These will not and cannot fix
the vulnerability on the source website, but will prevent the mobile
site from being used in an attack.

If a security issue is discovered in the client's website, the best
thing is of course to fix it at the source: to inform the client of
the issue, and convince them to take fast action to patch the security
hole. If this is done, no security accomodation is necessary on the
mobile site.

In practice, clients sometimes do not take such action for any number
of reasons, or are not willing or able to do so in a timely manner.
That is where this module comes in.  The aim is to render known
security exploits impossible to exercise through the mobile web
server.

Why do this at all, if it's the client's responsibility to begin with?

 - Out of service to the client, we owe it to them to provide the best
   product possible, which includes the most secure software we can
   provide given the circumstances.

 - As a practical measure, we normally cannot obtain PCI-DSS
   certification for the secure mobile site if any known web server
   exploit is possible THROUGH the mobile site at all.

 - If a security breach ever did occur due to a vulnerability in the
   desktop site, but using the mobile site as an intermediary, a
   result could be tremendous brand damage for Mobile Web Up; or
   litigation against Mobile Web Up by the client or other affected
   parties, which would be a great expense and distraction even in the
   event of a successful court defense.  This is especially true if
   credit card or other financial fraud occurs.  The fact that it
   would technically be the client's fault rather than Mobile Web Up's
   is immaterial.

For these reasons, we choose the view that it's NOT the client's fault
or responsibility; we make it OUR responsibility, as far as the
security of the client's mobile web presence is concerned.
 
'''
import re

class SecurityException(Exception):
    pass

class DropResponseSignal(SecurityException):
    pass

from collections import OrderedDict

class HeaderDict(OrderedDict):
    pass

def vulntag(*tags):
    '''
    Set tags of vulnerabilities addressed by a security filter
    '''
    def helper1(func):
        if not hasattr(func, '_vulntags'):
            func._vulntags = set()
            func._vulntags.update(tag.strip().lower() for tag in tags)
            return func
    return helper1

def get_vultags(func):
    return getattr(func, '_vulntags', set())

def nopoweredby(response_headers):
    '''
    Removes any X-Powered-By: response header

    This frustrates certain information disclosures that could inform possible attacks.
    
    '''
    if 'x-powered-by' in response_headers:
        del response_headers['x-powered-by']

@vulntag('cve-2000-0236')
def wptaglisting(get_param_keys : list):
    '''
    Directory listing through wp tag: wp-cs-dump and wp-ver-info 

    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2000-0236
    '''
    forbiddens = {
        'wp-cs-dump',
        'wp-ver-info',
        }
    if forbiddens.isdisjoint(get_param_keys):
        raise DropResponseSignal()

@vulntag(
    'cve-2004-0519',
    'cve-2004-0520',
    'cve-2004-0521',
    'cve-2004-1036',
    'cve-2005-1769',
    'cve-2005-2095',
    'cve-2006-3665',
    )
def squirrelmail_misc(rel_uri : str):
    '''
    Attempts to protect against or mitigate vulnerabilities related to older versions of Squirrelmail

    There are many possible vulnerabilities covered by this, including:

    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2004-0519
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2004-0520
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2004-0521
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2004-1036
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2005-1769
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2005-2095
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2006-3665

    The best solution is for the client to either upgrade or remove
    the old version of squirrelmail installed on their server hosting
    the full site.  If that is not happening, this security filter at
    least prevents some of its vulnerabilities from being
    exploited through the mobile site.
    
    '''
    # Drop requests to URLs related to squirrelmail
    # Example URL that discloses the installed squirrelmail version:
    #   http://m.example.com/mail/src/redirect.php?base_uri=squirrelmail_redirect_cookie_theft.nasl
    if rel_uri.startswith('/mail/src/redirect.php'):
        raise DropResponseSignal()

def phpinfo(rel_uri : str):
    '''
    Block a commonly used PHP info URL

    Some PHP-based servers in the wild will return a well-formatted
    information dump of the server's software and configuration with
    an HTTP request to /phpinfo.php .  As this provides a rich set of
    valuable information for an attacker, we want to block this.
    
    '''
    if rel_uri.startswith('/phpinfo.php'):
        raise DropResponseSignal()

def phpeastereggs(get_param_keys : list):
    '''
    Blocks some PHP easter eggs that might disclose info or otherwise enable an exploit
    More info at http://www.0php.com/php_easter_egg.php

    '''
    forbiddens = {
        'PHPB8B5F2A0-3C92-11d3-A3A9-4C7B08C10000',
        'PHPE9568F34-D428-11d2-A769-00AA001ACF42',
        'PHPE9568F35-D428-11d2-A769-00AA001ACF42',
        'PHPE9568F36-D428-11d2-A769-00AA001ACF42',
        }
    if forbiddens.isdisjoint(get_param_keys):
        raise DropResponseSignal()

@vulntag('cve-2004-0269')
def phpnuke(rel_uri: str):
    '''
    Protects against some phpnuke related vulnerabilites.

    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2004-0269
    '''
    if _phpnuke_sqlinjection_urlmatch(rel_uri):
        raise DropResponseSignal()

@vulntag('cve-2003-0043', 'cve-2003-0042')
def tomcatnull(rel_uri: list):
    '''
    Protects against some Tomcat directory listing/read priv escalation attacks
    
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2003-0043
    http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2003-0042
    '''
    if rel_uri.endswith('%00') or rel_uri.startswith('/cgi-bin/tomcat_proxy_directory_traversal'):
        raise DropResponseSignal()
        
# supporting code

def _phpnuke_sqlinjection_urlmatch(rel_uri: str):
    '''
    Check whether the relative uri matches some known phpnuke sql injection vectors
    '''
    regexes = map(re.compile, {
            r'(?i)^/modules.php\?.*select.*nuke_',
            r'(?i)^/index.php\?.*select.*nuke_authors',
            })

    return any(regex.search(rel_uri) is not None
               for regex in regexes)

