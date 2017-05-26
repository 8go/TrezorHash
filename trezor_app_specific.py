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

	Methods setAddress() and setIV() are usually called only at initialization.
	They create an address and an AES-CBS initialization vector.
	Address and IV are stored internally in the class to make the
	trezorEncryptHash() call simpler and with fewer parameters.

	In summary the encrypted hash is computed as follows:
	The 999th public receiving BTC address of account 0 of the Trezor wallet without
	passphrase is computed. From this address the MD5 hash is derived. This is a
	16-byte digest which will later be used as initial vector IV in the AES
	encryption.
	The input is a message in unicode UTF-8.
	A SHA256 hash is computed from this message.
	The resulting 32-byte digest is encrypted on the Trezor with AES CBC using
	the IV mentioned before. This encryption uses some static magic numbers
	as keys. The encryption is also influenced by the `confirm-on-Trezor-button`
	flags. This is why the output for running the program is different
	depending whether a `confirm-button` press is required or not.
	This encrypted byte array is also 32-bytes. It will be again hashed with
	SHA256 resulting in the final 32-byte, i.e. 256-bit, digest which is the
	final output. This outbut is converted into a hex string of 64 letters
	in the alphabet [0-9a-f]. This 64-letter string is returned to the caller.
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
		binoutput2 = hashlib.sha256(binoutput).digest()
		# length of binhash == length of binoutput == len of binoutput2 = 32
		# length of hexoutput == 64, length of stroutput == 64
		hexoutput = binascii.hexlify(binoutput2)
		stroutput = hexoutput.decode('utf-8')
		return stroutput
