from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import getpass
import logging

from trezorlib.client import ProtocolMixin
from trezorlib.transport_hid import HidTransport
from trezorlib.client import BaseClient  # CallException, PinException
from trezorlib import messages_pb2 as proto
from trezorlib.transport import ConnectionError

from trezor_gui import TrezorPassphraseDialog, EnterPinDialog, TrezorChooserDialog


class QtTrezorMixin(object):
	"""
	Mixin for input of Trezor PIN and passhprases.
	Works via both, terminal as well as PyQt GUI
	"""

	def __init__(self, *args, **kwargs):
		super(QtTrezorMixin, self).__init__(*args, **kwargs)
		self.passphrase = None
		self.readpinfromstdin = None
		self.readpassphrasefromstdin = None

	def callback_ButtonRequest(self, msg):
		return proto.ButtonAck()

	def callback_PassphraseRequest(self, msg):
		if self.passphrase is not None:
			return proto.PassphraseAck(passphrase=str(self.passphrase))

		if self.readpassphrasefromstdin:
			# read passphrase from stdin
			try:
				passphrase = getpass.getpass("Please enter passphrase: ")
				passphrase = str(passphrase)
			except KeyboardInterrupt:
				sys.stderr.write("\nKeyboard interrupt: passphrase not read. Aborting.\n")
				sys.exit(3)
			except Exception as e:
				sys.stderr.write("Critical error: Passphrase not read. Aborting. (%s)" % e)
				sys.exit(3)
		else:
			dialog = TrezorPassphraseDialog()
			if not dialog.exec_():
				sys.exit(3)
			else:
				passphrase = dialog.passphraseEdit.text()
				passphrase = str(passphrase)

		return proto.PassphraseAck(passphrase=passphrase)

	def callback_PinMatrixRequest(self, msg):
		if self.readpinfromstdin:
			# read PIN from stdin
			print("                  7  8  9")
			print("                  4  5  6")
			print("                  1  2  3")
			try:
				pin = getpass.getpass("Please enter PIN: ")
			except KeyboardInterrupt:
				sys.stderr.write("\nKeyboard interrupt: PIN not read. Aborting.\n")
				sys.exit(7)
			except Exception as e:
				sys.stderr.write("Critical error: PIN not read. Aborting. (%s)" % e)
				sys.exit(7)
		else:
			dialog = EnterPinDialog()
			if not dialog.exec_():
				sys.exit(7)
			pin = dialog.pin()

		return proto.PinMatrixAck(pin=pin)

	def prefillPassphrase(self, passphrase):
		"""
		Instead of asking for passphrase, use this one
		"""
		if passphrase is not None:
			self.passphrase = passphrase.decode("utf-8")
		else:
			self.passphrase = None

	def prefillReadpinfromstdin(self, readpinfromstdin=False):
		"""
		Specify if PIN should be read from stdin instead of from GUI
		@param readpinfromstdin: True to force it to read from stdin, False otherwise
		@type readpinfromstdin: C{bool}
		"""
		self.readpinfromstdin = readpinfromstdin

	def prefillReadpassphrasefromstdin(self, readpassphrasefromstdin=False):
		"""
		Specify if passphrase should be read from stdin instead of from GUI
		@param readpassphrasefromstdin: True to force it to read from stdin, False otherwise
		@type readpassphrasefromstdin: C{bool}
		"""
		self.readpassphrasefromstdin = readpassphrasefromstdin


class QtTrezorClient(ProtocolMixin, QtTrezorMixin, BaseClient):
	"""
	Trezor client with Qt input methods
	"""
	pass


class TrezorChooser(object):
	"""Class for working with Trezor device via HID"""

	def __init__(self, readdevicestringfromstdin=False):
		self.readdevicestringfromstdin = readdevicestringfromstdin

	def getDevice(self):
		"""
		Get one from available devices. Widget will be shown if more
		devices are available.
		"""
		devices = self.enumerateHIDDevices()
		if not devices:
			return None

		transport = self.chooseDevice(devices)
		client = QtTrezorClient(transport)
		return client

	def enumerateHIDDevices(self):
		"""Returns Trezor HID devices"""
		devices = HidTransport.enumerate()

		return devices

	def chooseDevice(self, devices):
		"""
		Choose device from enumerated list. If there's only one Trezor,
		that will be chosen.

		If there are multiple Trezors, diplays a widget with list
		of Trezor devices to choose from.

		@returns HidTransport object of selected device
		"""
		if not len(devices):
			raise RuntimeError("No Trezor connected!")

		if len(devices) == 1:
			try:
				return HidTransport(devices[0])
			except IOError:
				raise RuntimeError("Trezor is currently in use")

		# maps deviceId string to device label
		deviceMap = {}
		for device in devices:
			try:
				transport = HidTransport(device)
				client = QtTrezorClient(transport)
				label = client.features.label and client.features.label or "<no label>"
				client.close()

				deviceMap[device[0]] = label
			except IOError:
				# device in use, do not offer as choice
				continue

		if not deviceMap:
			raise RuntimeError("All connected Trezors are in use!")

		if self.readdevicestringfromstdin:
			print('Chose your Trezor device please. Devices currently in use are not listed:')
			ii = 0
			for device in deviceMap:
				print('%d  %s' % (ii, deviceMap[device]))
				ii += 1
			ii -= 1
			while True:
				inputstr = raw_input("Please provide the number of the device chosen: (%d-%d, Carriage return to quit) " % (0, ii))
				if inputstr == '':
					raise RuntimeError("No Trezors device chosen! Quitting.")
				try:
					inputint = int(inputstr)
				except Exception:
					print('Wrong input. You must enter a number between %d and %d. Try again.' % (0, ii))
					continue
				if inputint < 0 or inputint > ii:
					print('Wrong input. You must enter a number between %d and %d. Try again.' % (0, ii))
					continue
				break
			deviceStr = deviceMap.keys()[ii]
		else:
			dialog = TrezorChooserDialog(deviceMap)
			if not dialog.exec_():
				raise RuntimeError("No Trezors device chosen! Quitting.")
			deviceStr = dialog.chosenDeviceStr()

		return HidTransport([deviceStr, None])


def setupTrezor(readdevicestringfromstdin=False, mlogger=None):
	"""
	setup Trezor,
	on error exit program
	"""
	try:
		if mlogger is not None:
			mlogger.log("Starting Trezor initialization", logging.DEBUG, "Trezor Info")
		trezorChooser = TrezorChooser(readdevicestringfromstdin)
		trezor = trezorChooser.getDevice()
	except (ConnectionError, RuntimeError) as e:
		if mlogger is not None:
			mlogger.log("Connection to Trezor failed: %s" % e.message,
			logging.CRITICAL, "Trezor Error")
		sys.exit(1)

	if trezor is None:
		if mlogger is not None:
			mlogger.log("No available Trezor found, quitting.",
				logging.CRITICAL, "Trezor Error")
		sys.exit(1)
	return trezor
