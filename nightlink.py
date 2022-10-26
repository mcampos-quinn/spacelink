"""
This will be the nightly sync between cspace and resourcespace
"""

import sys

import config

cspace_instance = sys.argv[1]
if cspace_instance in config.CSPACE_BASEURL:
    # do stuff
    pass
