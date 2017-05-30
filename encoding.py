from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import struct
import unicodedata

"""
This is generic code that should work untouched accross all applications.
This code implements generic encoding functions.

Class Magic will need some minor customization for specific applications.

Code should work on both Python 2.7 as well as 3.4.
Requires PyQt5.
(Old version supported PyQt4.)
"""


def unpack(fmt, s):
	# 	u = lambda fmt, s: struct.unpack(fmt, s)[0]
	return(struct.unpack(fmt, s)[0])


def pack(fmt, s):
	# 	p = lambda fmt, s: struct.pack(fmt, s)[0]
	return(struct.pack(fmt, s))


def normalize_nfc(txt):
	"""
	Utility function to bridge Py2 and Py3 incompatibilities.
	Convert to NFC unicode.
	Takes string-equivalent or bytes-equivalent and
	returns str-equivalent in NFC unicode format.
	Py2: str (aslias bytes), unicode
	Py3: bytes, str (in unicode format)
	"""
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


def tobytes(txt):
	"""
	Utility function to bridge Py2 and Py3 incompatibilities.
	Convert to bytes.
	Takes string-equivalent or bytes-equivalent and returns bytesequivalent.
	Py2: str (aslias bytes), unicode
	Py3: bytes, str (in unicode format)
	"""
	if sys.version_info[0] < 3:
		if isinstance(txt, unicode):
			return txt.encode('utf-8')
		if isinstance(txt, str):  # == bytes
			return txt
	else:
		if isinstance(txt, bytes):
			return txt
		if isinstance(txt, str):
			return txt.encode('utf-8')


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


class Padding(object):
	"""
	PKCS#7 Padding for block cipher having 16-byte blocks
	"""

	def __init__(self, blocksize):
		self.blocksize = blocksize

	def pad(self, s):
		"""
		In Python 2 input s is a string, a char list.
		Python 2 returns a string.
		In Python 3 input s is bytes.
		Python 3 returns bytes.
		"""
		BS = self.blocksize
		if sys.version_info[0] > 2:
			return s + (BS - len(s) % BS) * bytes([BS - len(s) % BS])
		else:
			return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

	def unpad(self, s):
		if sys.version_info[0] > 2:
			return s[0:-s[-1]]
		else:
			return s[0:-ord(s[-1])]
