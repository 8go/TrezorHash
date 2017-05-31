from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging
import datetime
import traceback

from trezorlib.client import CallException, PinException

"""
This file holds the main business logic.
It should be shared by the GUI mode and the Terminal mode.
"""


def doWork(teh, settings, dialog=None):
	"""
	Do the real work, perform the main business logic.
	Input comes from settings.
	Output goes to settings.
	This function should be shared by GUI mode and Terminal mode.

	@param teh: object holding the trezor logic
	@type teh: L{trezor_app_specific.TrezorEncryptedHash}
	@param settings: holds settings for how to log info/warnings/errors,
		also holds the mlogger
	@type settings: L{Settings}
	@param dialog: holds GUI window for where to log info/warnings/errors
	@type dialog: L{dialogs.Dialog}
	"""

	settings.mlogger.log("Time entering doWork(): %s" % datetime.datetime.now(),
		logging.DEBUG, "Debug")
	try:
		if settings.TArg:
			print("Input:  '%s'" % settings.input)
		else:
			settings.mlogger.log(u"Input:  '%s'" % settings.input,
				logging.DEBUG, "Processing")
		settings.output = teh.trezorEncryptHash(settings.input)
		settings.outputshort = settings.output[0:3] + "..." + settings.output[-3:]
		if settings.TArg:
			print("Output: '%s'" % settings.output)
		settings.mlogger.log("Output short: '%s'" % settings.outputshort,
			logging.DEBUG, "Processing")
	except PinException:
		settings.mlogger.log("Trezor reports invalid PIN. Aborting.",
			logging.CRITICAL, "Trezor IO")
		sys.exit(8)
	except CallException:
		# button cancel on Trezor, so exit
		settings.mlogger.log("Trezor reports that user clicked 'Cancel' "
			"on Trezor device. Aborting.", logging.CRITICAL, "Trezor IO")
		sys.exit(6)
	except IOError as e:
		settings.mlogger.log("IO error: %s" % e,
			logging.CRITICAL, "Critical Exception")
		if settings.logger.getEffectiveLevel() == logging.DEBUG:
			traceback.print_exc()  # prints to stderr
	except Exception as e:
		settings.mlogger.log("Critical error: %s" % e,
			logging.CRITICAL, "Critical Exception")
		if settings.logger.getEffectiveLevel() == logging.DEBUG:
			traceback.print_exc()  # prints to stderr
	settings.mlogger.log("Time leaving doWork(): %s" % datetime.datetime.now(),
		logging.DEBUG, "Debug")


def processAll(teh, settings, dialog=None):
	"""
	Do the real work, perform the main business logic.
	Input comes from settings (Terminal mode) or dialog (GUI mode).
	Output goes to settings (Terminal mode) or dialog (GUI mode).
	This function should be shared by GUI mode and Terminal mode.

	If dialog is None then processAll() has been called
	from Terminal and there is no GUI.
	If dialog is not None processAll() has been called
	from GUI and there is a window.

	Input is in settings.input,
	Output will be placed in settings.output.

	@param teh: object holding the trezor logic
	@type teh: L{trezor_app_specific.TrezorEncryptedHash}
	@param settings: holds settings for how to log info/warnings/errors
		used to hold inputs and outputs
	@type settings: L{Settings}
	@param dialog: holds GUI window for access to GUI input, output
	@type dialog: L{dialogs.Dialog}
	"""
	if dialog is not None:
		settings.mlogger.log("Apply button was clicked",
			logging.DEBUG, "Debug")
		settings.gui2Settings(dialog)  # move input from GUI to settings
	doWork(teh, settings, dialog)
	if dialog is not None:
		settings.settings2Gui(dialog)  # move output from settings to GUI
		settings.mlogger.log("Apply button was processed, returning to GUI",
			logging.DEBUG, "Debug")
