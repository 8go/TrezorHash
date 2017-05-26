from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import struct
import unicodedata

from PyQt4 import QtCore


def q2s(q):
	"""Convert QString to UTF-8 string object"""
	return str(q.toUtf8()).decode('utf-8')


def s2q(s):
	"""Convert UTF-8 encoded string to QString"""
	return QtCore.QString.fromUtf8(s)


def u(fmt, s):
	# 	u = lambda fmt, s: struct.unpack(fmt, s)[0]
	return(struct.unpack(fmt, s)[0])


def p(fmt, s):
	# 	u = lambda fmt, s: struct.unpack(fmt, s)[0]
	return(struct.pack(fmt, s))


def normalize_nfc(txt):
	if sys.version_info[0] < 3:
		if isinstance(txt, unicode):
			return unicodedata.normalize('NFC', txt)
		if isinstance(txt, str):
			return unicodedata.normalize('NFC', txt.decode('utf-8'))
	else:
		if isinstance(txt, bytes):
			return unicodedata.normalize('NFC', txt.decode('utf-8'))
		if isinstance(txt, str):
			return unicodedata.normalize('NFC', txt)


class Magic(object):
	"""
	Few magic constant definitions so that we know which nodes to search
	for keys.
	"""

	headerStr = b'TRZR'
	hdr = u("!I", headerStr)

	# to encrypt hash
	hashNode = [hdr, u("!I", b'HASH')]
	hashKey = "Allow  HASH      encryption?"  # string to encrypt hash


class Padding(object):
	"""
	PKCS#7 Padding for block cipher having 16-byte blocks
	"""

	def __init__(self, blocksize):
		self.blocksize = blocksize

	def pad(self, s):
		BS = self.blocksize
		return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

	def unpad(self, s):
		return s[0:-ord(s[-1])]
