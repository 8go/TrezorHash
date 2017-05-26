from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging
import datetime
import traceback

from trezorlib.client import CallException, PinException


def doWork(teh, settings, dialog):
	"""
	Loop through the list of filenames in `settings`
	and process each one.

	@param settings: holds settings for how to log info/warnings/errors
	@type settings: L{Settings}
	@param fileMap: object to use to handle file format of encrypted file
	@type fileMap: L{file_map.FileMap}
	@param logger: holds logger for where to log info/warnings/errors
	@type logger: L{logging.Logger}
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
	If dialog is None then processAll() has been called
	from Terminal and there is no GUI.
	If dialog is not None processAll() has been called
	from GUI and there is a window.

	Input is in settings.input,
	output will be placed in settings.output.

	@param settings: holds settings for how to log info/warnings/errors
	@type settings: L{Settings}
	@param teh: object to use to handle Trezor work
	@type fileMap: L{trezor_app_specific.TrezorEncryptedHash}
	@param dialog: holds GUI window for access to GUI input, output
	@type dialog: L{dialogs.Dialog}
	"""
	if dialog is not None:
		settings.mlogger.log("Apply button was clicked",
			logging.DEBUG, "Debug")
		settings.gui2Settings(dialog)
	doWork(teh, settings, dialog)
	if dialog is not None:
		settings.settings2Gui(dialog)
		settings.mlogger.log("Apply button was processed, returning to GUI",
			logging.DEBUG, "Debug")
