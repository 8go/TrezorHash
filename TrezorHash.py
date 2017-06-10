#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging
import codecs

from PyQt5.QtWidgets import QApplication  # for the clipboard and window

from dialogs import Dialog

import basics
import utils
import settings
import encoding
import processing
from trezor_app_specific import TrezorEncryptedHash
import trezor_app_generic

"""
The file with the main function.

Code should work on both Python 2.7 as well as 3.4.
Requires PyQt5.
(Old version supported PyQt4.)
"""


def showGui(trezor, dialog, settings):
	"""
	Display input from command line or from clipboard
	as suggested input,
	read input string
	read button clicks
	display shortened result
	place output on clipboard

	Makes sure a session is created on Trezor.

	@param trezor: Trezor client
	@param dialog: the GUI window
	@param settings: Settings object to store input and output
		also holds any necessary settings
	"""
	settings.settings2Gui(dialog)
	if not dialog.exec_():
		# Esc or exception or Quit/Close/Done
		settings.mlogger.log("Shutting down due to user request "
			"(Done/Quit was called).", logging.DEBUG, "GUI IO")
		# sys.exit(4)
	settings.gui2Settings(dialog)


def useTerminal(teh, settings):
	# Clipboard only works if there is a GUI window.
	# In text-only mode one cannot interact with the keyboard.
	# In text only mode one can only read from clipboard, but not write to it.
	# Package pyperclip also does not work without a GUI.
	# No clipboard in terminal mode.
	for ii in range(settings.inputArgs.count('')):
		settings.inputArgs.remove('')  # get rid of all empty strings
	if len(settings.inputArgs) == 0:
		settings.input = utils.input23(u"Please provide an input string to be hashed: "
			"(Carriage return to quit) ")
		# convert all input as possible to unicode UTF-8 NFC
		settings.input = encoding.normalize_nfc(settings.input)
		if settings.input == "":
			settings.mlogger.log(u"User decided to abandon.", logging.DEBUG,
				u"User IO")
			sys.exit(3)
		settings.inputArgs.append(settings.input)
	for item in settings.inputArgs:
		if item != "":  # double-check
			settings.input = item
			processing.processAll(teh, settings)


def main():
	if sys.version_info[0] < 3:  # Py2-vs-Py3:
		# redirecting output to a file can cause unicode problems
		# read: https://stackoverflow.com/questions/5530708/
		# To fix it either run the scripts as: PYTHONIOENCODING=utf-8 python TrezorHash.py
		# or add the following line of code.
		# Only shows up in python2 TrezorHash.py >> log scenarios
		# Exception: 'ascii' codec can't encode characters in position 10-13: ordinal not in range(128)
		sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

	app = QApplication(sys.argv)
	sets = settings.Settings()  # initialize settings
	# parse command line
	args = settings.Args(sets)
	args.parseArgs(sys.argv[1:])

	trezor = trezor_app_generic.setupTrezor(sets.TArg, sets.mlogger)
	# trezor.clear_session() ## not needed
	trezor.prefillReadpinfromstdin(sets.TArg)
	trezor.prefillReadpassphrasefromstdin(sets.TArg)
	trezor.prefillPassphrase(u'')

	if sets.TArg:
		sets.mlogger.log(u"Terminal mode --terminal was set. Avoiding GUI.",
			logging.INFO, u"Arguments")
		dialog = None
	else:
		dialog = Dialog(trezor, sets)
		sets.mlogger.setQtextbrowser(dialog.textBrowser)
		sets.mlogger.setQtextheader(dialog.descrHeader())
		sets.mlogger.setQtextcontent(dialog.descrContent())
		sets.mlogger.setQtexttrailer(dialog.descrTrailer())

	# if there is no command line input, check the clipboard
	if sets.input is None:
		clipboard = app.clipboard()
		sets.input = encoding.normalize_nfc(clipboard.text())
		if sets.input != '':
			sets.mlogger.log("No argument given on command line, "
				"took input from clipboard.", logging.INFO,
				"Arguments")
		else:
			sets.mlogger.log("Neither command line nor "
				"clipboard provided input.", logging.INFO,
				"Arguments")
		sets.inputArgs.append(sets.input)
		del clipboard

	sets.mlogger.log("Trezor label: %s" % trezor.features.label,
		logging.INFO, "Trezor IO")
	sets.mlogger.log("Click 'Confirm' on Trezor to give permission "
		"each time you hash a message.", logging.INFO, "Trezor IO")

	teh = TrezorEncryptedHash(trezor, sets)

	if sets.TArg:
		useTerminal(teh, sets)
	else:
		# user wants GUI, so we call the GUI
		dialog.setTeh(teh)
		dialog.setVersion(basics.VERSION_STR)
		showGui(trezor, dialog, sets)
		dialog.clipboard.setText(u' ' * 128)
		dialog.clipboard.clear()
		del dialog.clipboard  # important to avoid warning on stdout
	# cleanup
	sets.mlogger.log("Cleaning up before shutting down.", logging.DEBUG, "Info")
	trezor.close()


if __name__ == '__main__':
	main()
