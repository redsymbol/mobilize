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
