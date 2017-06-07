from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
from encoding import unpack

"""
This file contains some constant variables like version numbers,
default values, etc.
"""

# Name of application
NAME = u'TrezorHash'

# Name of software version
VERSION_STR = u'v0.5.2-beta'

# Date of software version
VERSION_DATE_STR = u'June 2017'

# default log level
DEFAULT_LOG_LEVEL = logging.INFO  # CRITICAL, ERROR, WARNING, INFO, DEBUG

# short acronym used for name of logger
LOGGER_ACRONYM = u'th'

# location of logo image
LOGO_IMAGE = u"icons/TrezorHash.92x128.png"


class Magic(object):
	"""
	Few magic constant definitions so that we know which nodes to search
	for keys.
	"""

	headerStr = b'TRZR'
	hdr = unpack("!I", headerStr)

	# to encrypt hash
	hashNode = [hdr, unpack("!I", b'HASH')]
	hashKey = b"Allow  HASH      encryption?"  # string to encrypt hash
