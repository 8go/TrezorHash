from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging
import getopt

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR

import basics
import encoding
from utils import BaseSettings, BaseArgs

"""
This is code that should be adapted to your applications.
This code implements Settings and Argument parsing.

Classes BaseSettings and BaseArgs from utils.py
should be subclassed her as Settings and Args.

Code should work on both Python 2.7 as well as 3.4.
Requires PyQt5.
(Old version supported PyQt4.)
"""


class Settings(BaseSettings):
	"""
	Placeholder for settings
	Settings such as command line options, GUI selected values,
	user input, etc.
	"""

	def __init__(self, logger=None, mlogger=None):
		"""
		@param logger: holds logger for where to log info/warnings/errors
			If None, a default logger will be created.
		@type logger: L{logging.Logger}
		@param mlogger: holds mlogger for where to log info/warnings/errors
			If None, a default mlogger will be created.
		@type mlogger: L{utils.MLogger}
		"""
		super(Settings, self).__init__(logger, mlogger)
		self.TArg = False
		self.MArg = False
		self.NArg = False
		self.input = None
		self.output = None
		self.outputshort = None
		self.inputArgs = []  # list of input strings

	def logSettings(self):
		self.logger.debug(self.__str__())

	def gui2Settings(self, dialog):
		"""
		This method should be implemented in the subclass.
		Copy the settings info from the dialog GUI to the Settings instance.
		"""
		self.input = dialog.input()

	def settings2Gui(self, dialog):
		"""
		This method should be implemented in the subclass.
		Copy the settings info from the Settings instance to the dialog GUI.
		"""
		dialog.setInput(self.input)
		dialog.setOutput(self.outputshort)
		dialog.clipboard.setText(self.output)

	def __str__(self):
		return(super(Settings, self).__str__() + "\n" +
			"settings.TArg = %s\n" % self.TArg +
			"settings.MArg = %s\n" % self.MArg +
			"settings.NArg = %s\n" % self.NArg +
			"settings.input = %s\n" % self.input +
			"settings.outputshort = %s\n" % self.outputshort +
			"settings.output = %s\n" % u'***' +
			"settings.inputArgs = %s" % self.inputArgs)


class Args(BaseArgs):
	"""
	CLI Argument handling
	"""

	def __init__(self, settings, logger=None):
		"""
		Get all necessary parameters upfront, so the user
		does not have to provide them later on each call.

		@param settings: place to store settings
		@type settings: L{Settings}
		@param logger: holds logger for where to log info/warnings/errors
			if no logger is given it uses the default logger of settings.
			So, usually this would be None.
		@type logger: L{logging.Logger}
		"""
		super(Args, self).__init__(settings, logger)

	def printVersion(self):
		super(Args, self).printVersion()

	def printUsage(self):
		print('''TrezorHash.py [-h] [-v] [-t [-m]] [-l <loglevel>] [-n] [<input> [<inputs>]]
		This program takes an input message via CLI, clipboard or GUI, and
		deterministically creates a Trezor-specific encrypted hash (digest).
		For the same 24 Trezor seeds, independent of passphrase and other
		parameters, it always returns the same output.
		It is a one-way function. One cannot compute the input given the output.
		Output length is always the same, 64 letters from alphabet [a-z0-9].
		The output digest has 256 bits.
		Different inputs will with near-vcertainty lead to different outputs.
		The output is difficult to guess or brute-force.
		In GUI mode the output is never written to a file or storage. It remains
		only in memory. It is passed to the user exclusively via the clipboard.
		When the GUI is closed, the clipboard is automatically overwritten
		and cleared. So, the output digest must be pasted before closing
		the GUI.

		Possible use-cases of TrezorHash include:
		* Pseudorandom bit generation
		* Key derivation:
			Convenient tool to convert a simple, short, and easy to remember
			string into a long string that is very difficult to guess or brute-force
		* Password verification:
			Allows you to know if inputs are the same without knowing the input values,
			a useful piece for password management
		* Data identity and data integrity:
			Create personal digital signatures of short texts like emails.

		-v, --version
				Print the version number
		-h, --help
			Print help text
		-l, --logging
			Set logging level, integer from 1 to 5, 1=full logging, 5=no logging
		-t, --terminal
				Run in the terminal, this avoids the GUI. In terminal mode the
				output is written to stdout
		-m, --multiple
				With `-m` in terminal mode instead of one input, multiple
				input strings can be given as command line arguments for batch
				processing.
		-n, --noconfirm
				Eliminates the `Confirm` click on the Trezor button. Useful for
				batch processing. Be very aware that for security reasons
				the resulting output digest is *different* if `-n` is used!
		<input>
				Message, a string, to be hashed and encrypted.
				If no input is given then program will look at the clipboard for input.
				If input argument is missing and clipboard is empty program will ask
				user for input.

		Example usage:
		TrezorHash.py -t a
		Input:  "a"
		Output: "01dc56a86a759a00f4bf1b7e43789092ec197ed302ee799e11eaa18106f84e03"

		TrezorHash.py -t -n a # note the different output!
		Input:  "a"
		Output: "c038754a62b903e2a4630b9cedf562e9711cc36c1faef39c2c11c334042686ea"

		TrezorHash.py
		Input:  "Easy to remember"
		Output: "626020f7a90752f40abdff004861359b267caf3db7c15d64b1e38dd3cfa5e45d"

		Keyboard shortcuts of GUI:
		Apply, Hash: Control-A, Control-S
		Cancel, Quit: Esc, Control-Q
		Version, About: Control-T

		Requires: python 2.7 or 3.4+ and PyQt5 and trezorlib library.
		Tested on Linux on Python 2.7 and 3.4.

		BTW, for testing 'xsel -bi', 'xsel -bo' and 'xsel -bc' set, write and clear the clipboard on Linux.

		''')

	def parseArgs(self, argv, settings=None, logger=None):
		"""
		Parse the command line arguments and store the results in `settings`.
		Report errors to `logger`.

		@param settings: place to store settings;
			if None the default settings from the Args class will be used.
			So, usually this argument would be None.
		@type settings: L{Settings}
		@param logger: holds logger for where to log info/warnings/errors
			if None the default logger from the Args class will be used.
			So, usually this argument would be None.
		@type logger: L{logging.Logger}
		"""
		# do not call super class parseArgs as partial parsing does not work
		# superclass parseArgs is only useful if there are just -v -h -l [level]
		# get defaults
		if logger is None:
			logger = self.logger
		if settings is None:
			settings = self.settings
		try:
			opts, args = getopt.getopt(argv, "vhl:tmn",
				["version", "help", "logging=", "terminal", "multiple", "noconfirm"])
		except getopt.GetoptError as e:
			logger.critical(u'Wrong arguments. Error: %s.', e)
			try:
				msgBox = QMessageBox(QMessageBox.Critical, u"Wrong arguments",
					u"Error: %s" % e)
				msgBox.exec_()
			except Exception:
				pass
			sys.exit(2)
		loglevelused = False
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				self.printUsage()
				sys.exit()
			elif opt in ("-v", "--version"):
				self.printVersion()
				sys.exit()
			elif opt in ("-l", "--logging"):
				loglevelarg = arg
				loglevelused = True
			elif opt in ("-t", "--terminal"):
				settings.TArg = True
			elif opt in ("-m", "--multiple"):
				settings.MArg = True
			elif opt in ("-n", "--noconfirm"):
				settings.NArg = True

		if loglevelused:
			try:
				loglevel = int(loglevelarg)
			except Exception as e:
				self.settings.mlogger.log(u"Logging level not specified correctly. "
					"Must be integer between 1 and 5. (%s)" % loglevelarg, logging.CRITICAL,
					"Wrong arguments", settings.TArg, logger)
				sys.exit(18)
			if loglevel > 5 or loglevel < 1:
				self.settings.mlogger.log(u"Logging level not specified correctly. "
					"Must be integer between 1 and 5. (%s)" % loglevelarg, logging.CRITICAL,
					"Wrong arguments", settings.TArg, logger)
				sys.exit(19)
			settings.LArg = loglevel * 10  # https://docs.python.org/2/library/logging.html#levels
		logger.setLevel(settings.LArg)

		for arg in args:
			# convert all input as possible to unicode UTF-8 NFC
			settings.inputArgs.append(encoding.normalize_nfc(arg))
		if settings.MArg and not settings.TArg:
			self.settings.mlogger.log(u"Multiple inputs can only be used "
				"in terminal mode. Add '-t' or remove '-m'.",
				logging.CRITICAL, "Wrong arguments", True, logger)
			sys.exit(2)
		if len(args) >= 1:
			settings.input = args[0]
		if not settings.MArg and len(args) > 1:
			self.settings.mlogger.log(u"You cannot specify more than one "
				"input (unless you use '-t -m'). (%s)" % str(args),
				logging.CRITICAL, "Wrong arguments", True, logger)
			sys.exit(2)
		settings.mlogger.setTerminalMode(settings.TArg)
		self.settings.mlogger.log(u"%s Version: %s (%s)" %
			(basics.NAME, basics.VERSION, basics.VERSION_STR),
			logging.INFO, "Version", True, logger)
		self.settings.mlogger.log(u"Python: %s" % sys.version.replace(" \n", "; "),
			logging.INFO, "Version", True, logger)
		self.settings.mlogger.log(u"Qt Version: %s" % QT_VERSION_STR,
			logging.INFO, "Version", True, logger)
		self.settings.mlogger.log(u"PyQt Version: %s" % PYQT_VERSION_STR,
			logging.INFO, "Version", True, logger)
		self.settings.mlogger.log(u'Logging level set to %s (%d).' %
			(logging.getLevelName(settings.LArg), settings.LArg),
			logging.INFO, "Logging", True, logger)
		self.settings.mlogger.log(settings,
			logging.DEBUG, "Settings", True, logger)
