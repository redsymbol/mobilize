Mobilize - framework for creating smartphone-optimized versions of full websites

Mobilize is a platform for creating smartphone-friendly websites which
source their content from an existing, full-size website. The
resulting mobile view:

 * Immedidately and automatically updates its
   content as the source pages change
 * Includes automatic mobile optimizations like image resizing
   and substitution
 * Allows arbitrary modification, re-ordering, addition or deletion
  of content for the mobile view
 * Is compatible with every CMS, web framework and stack.

Mobilize itself is written in Python 3.4, and implemented as a
secondary proxy webserver that runs in Linux (in
Apache/mod_wsgi). Note, however, that it works with websites
implemented in any language, running on any stack and operating
system. Mobilize can run on the same machine, alongside your main web
server process - or if needed, a different one.

The current source code is not enough to get up and running; I am in
the process of bringing all the dependencies in.  Some things that are
currently missing include the image resizing server, device detection
service, and some essential documentation (on everything from
installation and configuration, to actual mobile development using the
framework.)

DOCUMENTATION

Is in progress.

REQUIREMENTS

Designed to work with Python 3.4 or higher.

LEGAL

Copyright 2011-2014 Aaron Maxwell (amax@redsymbol.net).

Licenced under GPL v. 3.

