from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import binascii
import logging

import encoding


class TrezorEncryptedHash(object):
	"""
	class that does the Trezor hash encryption
	"""

	def __init__(self, trezor, settings):
		self.trezor = trezor
		self.settings = settings
		self.baddress = None
		self.iv = None
		self.setAddress()
		self.setIv()

	def setAddress(self):
		"""
		# Get the first address of first BIP44 account
		# This is the main wallet address.
		# k-th account
		# i-th keypair
		# receive address
		# bip32_path = client.expand_path("44'/0'/k'/0/i")
		"""
		bip32_path = self.trezor.expand_path("44'/0'/0'/0/0")
		# API is: def get_address(self, coin_name, n, show_display=False, multisig=None, script_type=types.SPENDADDRESS):
		baddress = self.trezor.get_address('Bitcoin', bip32_path)
		# Address 0 is just for reference or confirmation, it is not used
		self.settings.mlogger.log("Main Bitcoin address: %s" % baddress,
			logging.DEBUG, "Trezor IO")
		bip32_path = self.trezor.expand_path("44'/0'/0'/0/999")  # addr 999
		baddress = self.trezor.get_address('Bitcoin', bip32_path)
		self.baddress = baddress

	def setIv(self):
		"""
		compute a Trezor specific Iv
		later used in Trezor encryption
		"""
		# IV : 16 bytes
		# compute IV as 16-byte MD5 hash of main BTC address
		iv = hashlib.md5(self.baddress.encode('utf-8')).digest()
		if len(iv) != 16:
			self.settings.mlogger.log("IV length not 16 bytes. Aborting.",
				logging.CRITICAL, "Internal Error")
			raise RuntimeError("IV length not 16 bytes.")
		self.iv = iv

	def trezorEncryptHash(self, input):
		"""
		Take a unicode string as input
		Hash it
		and then encrypt it
		return the output
		"""
		# hash the input with sha256
		# sha256 has a digest of 256 bits, 32 bytes
		# binary representation: 32 bytes:: len(binhash) == 32
		# hex representation: 64 letters, 64 bytes
		# hexhash = hashlib.sha256(input.encode('utf-8')).hexdigest()
		# print("hexhash %d" % len(hexhash)) ==> 64; hexhash.encode('utf-8') ==> 64

		# convert unicode to byes and compute sha256 hash
		binhash = hashlib.sha256(input.encode('utf-8')).digest()
		# hash is already padded because it is always 64 (multiple of 16)
		# WARNING: changing of ANY parameter will change the result!
		# AES encrypt the hash on the Trezor
		binoutput = self.trezor.encrypt_keyvalue(encoding.Magic.hashNode,
			encoding.Magic.hashKey, binhash,
			ask_on_encrypt=(not self.settings.NArg), ask_on_decrypt=True,
			iv=self.iv)
		# length of binhash == length of binoutput == 32, length of hexoutput == 64, length of stroutput == 64
		hexoutput = binascii.hexlify(binoutput)
		stroutput = hexoutput.decode('utf-8')
		return stroutput
