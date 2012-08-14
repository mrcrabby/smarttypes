"""
====================
Modules
====================

Modules are stored in a global dict, and loaded from the top down.

Module (x) may load another module (y)

If y then loads x (a cross-reference) it will only have the
parts of x that were loaded when itself (y) was called by x



====================
This app
====================

mod_wsgi loads wsgi.py

wsgi.py imports this, which should import everything else
"""

import os
from config import DB_USER, DB_PASSWORD
connection_string = "host=localhost dbname='smarttypes' user='%s' password='%s'" % (DB_USER, DB_PASSWORD)
root_dir = os.path.dirname(os.path.abspath(__file__))

site_name = 'SmartTypes'
site_mantra = 'a tool for social discovery.'
default_title = '%s - %s' % (site_name, site_mantra)
site_description = """
SmartTypes is an open lab for online social network analysis (initially twitter).
Our goal is to provide accurate maps of our social world."""
site_description = site_description.strip()

#keep these down here
import utils  # need this
import model  # need this
import controllers  # need this


