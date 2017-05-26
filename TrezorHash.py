#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging

from PyQt4 import QtGui  # for the clipboard and window

from dialogs import Dialog

import basics
import utils
import encoding
import processing
from trezor_app_specific import TrezorEncryptedHash
import trezor_app_generic


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
		settings.input = raw_input("Please provide an input string to be hashed: "
			"(Carriage return to quit) ")
		# convert all input as possible to unicode UTF-8
		settings.input = settings.input.decode('utf-8')
		if settings.input == "":
			settings.mlogger.log("User decided to abandon.", logging.DEBUG,
				"Trezor IO")
			sys.exit(3)
		settings.inputArgs.append(settings.input)
	for item in settings.inputArgs:
		if item != "":  # double-check
			settings.input = item
			processing.processAll(teh, settings)


def main():
	settings = utils.Settings()  # initialize settings
	# parse command line
	args = utils.Args(settings)
	args.parseArgs(sys.argv[1:])
	myapp = QtGui.QApplication([])

	trezor = trezor_app_generic.setupTrezor(settings.TArg, settings.mlogger)
	# trezor.clear_session() ## not needed
	trezor.prefillReadpinfromstdin(settings.TArg)
	trezor.prefillReadpassphrasefromstdin(settings.TArg)
	trezor.prefillPassphrase(u'')

	if settings.TArg:
		settings.mlogger.log("Terminal mode --terminal was set. Avoiding GUI.",
			logging.INFO, "Arguments")
		dialog = None
	else:
		dialog = Dialog(trezor, settings)
		settings.mlogger.setQtextbrowser(dialog.textBrowser)
		settings.mlogger.setQtextheader(dialog.descrHeader())
		settings.mlogger.setQtextcontent(dialog.descrContent())
		settings.mlogger.setQtexttrailer(dialog.descrTrailer())

	# if there is no command line input, check the clipboard
	if settings.input is None:
		clipboard = myapp.clipboard()
		settings.input = encoding.q2s(clipboard.text())
		if settings.input != '':
			settings.mlogger.log("No argument given on command line, "
				"took input from clipboard.", logging.INFO,
				"Arguments")
		else:
			settings.mlogger.log("Neither command line nor "
				"clipboard provided input.", logging.INFO,
				"Arguments")
		settings.inputArgs.append(settings.input)
		del clipboard

	settings.mlogger.log("Trezor label: %s" % trezor.features.label,
		logging.INFO, "Trezor IO")
	settings.mlogger.log("Click 'Confirm' on Trezor to give permission "
		"each time you produce hash.", logging.INFO, "Trezor IO")

	teh = TrezorEncryptedHash(trezor, settings)

	if settings.TArg:
		useTerminal(teh, settings)
	else:
		# user wants GUI, so we call the GUI
		dialog.setTeh(teh)
		dialog.setVersion(basics.THVERSION)
		showGui(trezor, dialog, settings)
		dialog.clipboard.setText(u' ' * 128)
		dialog.clipboard.clear()
		del dialog.clipboard  # important to avoid warning on stdout
	# cleanup
	settings.mlogger.log("Cleaning up before shutting down.", logging.DEBUG, "Info")
	trezor.close()


if __name__ == '__main__':
	main()
