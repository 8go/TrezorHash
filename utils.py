from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import logging
import getopt

from PyQt4 import QtGui

import basics
import encoding


class MLogger(object):
	"""
	class for logging that covers, print, logger, and writing to GUI QTextBrowser widget.
	Its is called *M*Logger because it can log to *M*ultiple streams
	such as stdout, QTextBrowser, msgBox, ...
	"""

	def __init__(self, terminalMode=None, logger=None, qtextbrowser=None):
		"""
		Get as many necessary parameters upfront as possible, so the user
		does not have to provide them later on each call.

		@param terminalMode: log only to terminal?
		@type terminalMode: C{bool}
		@param logger: holds logger for where to log info/warnings/errors
		@type logger: L{logging.Logger}
		@param qtextbrowser: holds GUI widget for where to log info/warnings/errors
		@type qtextbrowser: L{QtGui.QTextBrowser}
		"""
		self.terminalMode = terminalMode
		self.logger = logger
		self.qtextbrowser = qtextbrowser
		# qtextbrowser text will be created by assembling:
		# qtextheader + qtextContent + qtextTrailer
		self.qtextheader = u''
		self.qtextcontent = u''
		self.qtexttrailer = u''

	def setTerminalMode(self, terminalMode):
		self.terminalMode = terminalMode

	def setLogger(self, logger):
		self.logger = logger

	def setQtextbrowser(self, qtextbrowser):
		"""
		@param qtextbrowser: holds GUI widget for where to log info/warnings/errors
		@type qtextbrowser: L{QtGui.QTextBrowser}
		"""
		self.qtextbrowser = qtextbrowser

	def setQtextheader(self, str):
		"""
		@param str: string to report/log
		@type str: C{string}
		"""
		self.qtextheader = str

	def setQtextcontent(self, str):
		"""
		@param str: string to report/log
		@type str: C{string}
		"""
		self.qtextcontent = str

	def appendQtextcontent(self, str):
		"""
		@param str: string to report/log
		@type str: C{string}
		"""
		self.qtextcontent += str

	def setQtexttrailer(self, str):
		"""
		@param str: string to report/log
		@type str: C{string}
		"""
		self.qtexttrailer = str

	def qtext(self):
		return self.qtextheader + self.qtextcontent + self.qtexttrailer

	def moveCursorToBottomQtext(self):
		# move the cursor to the end of the text, scroll to the bottom
		cursor = self.qtextbrowser.textCursor()
		cursor.setPosition(len(self.qtextbrowser.toPlainText()))
		self.qtextbrowser.ensureCursorVisible()
		self.qtextbrowser.setTextCursor(cursor)

	def publishQtext(self):
		self.qtextbrowser.setHtml(encoding.s2q(self.qtext()))
		self.moveCursorToBottomQtext()

	def log(self, str, level, title, terminalMode=None, logger=None, qtextbrowser=None):
		"""
		Displays string `str` depending on scenario:
		a) in terminal mode: thru logger (except if loglevel == NOTSET)
		b) in GUI mode and GUI window open: (qtextbrowser!=None) in qtextbrowser of GUI window
		c) in GUI mode but window still/already closed: (qtextbrowser==None) thru QMessageBox()

		If terminalMode=None, logger=None, qtextbrowser=None, then the
		corresponding value from self is used. So, None means this
		value should default to the preset value of the class Log.

		@param str: string to report/log
		@type str: C{string}
		@param level: log level from DEBUG to CRITICAL from L{logging}
		@type level: C{int}
		@param title: window title text (only used if there is a window)
		@type title: C{string}

		@param terminalMode: log only to terminal?
		@type terminalMode: C{bool}
		@param logger: holds logger for where to log info/warnings/errors
		@type logger: L{logging.Logger}
		@param qtextbrowser: holds GUI widget for where to log info/warnings/errors
		@type qtextbrowser: L{QtGui.QTextBrowser}
		"""
		# get defaults
		if terminalMode is None:
			terminalMode = self.terminalMode
		if logger is None:
			logger = self.logger
		if qtextbrowser is None:
			qtextbrowser = self.qtextbrowser
		# initialize
		if logger is None:
			logging.basicConfig(stream=sys.stderr, level=basics.DEFAULTLOGLEVEL)
			logger = logging.getLogger(basics.LOGGERACRONYM)
		if qtextbrowser is None:
			guiExists = False
		else:
			guiExists = True
		if guiExists:
			if terminalMode is None:
				terminalMode = False
		else:
			if terminalMode is None:
				terminalMode = True
		if level == logging.NOTSET:
			if terminalMode:
				print(str)  # stdout
			elif guiExists:
				print(str)  # stdout
				self.appendQtextcontent(u"<br>%s" % (str))
			else:
				print(str)  # stdout
				msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information,
					title, u"%s" % (str))
				msgBox.exec_()
		elif level == logging.DEBUG:
			if terminalMode:
				logger.debug(str)
			elif guiExists:
				logger.debug(str)
				if logger.getEffectiveLevel() <= level:
					self.appendQtextcontent(u"<br>Debug: %s" % str)
			else:
				# don't spam the user with too many pop-ups
				# For debug, instead of a pop-up we write to stdout
				logger.debug(str)
		elif level == logging.INFO:
			if terminalMode:
				logger.info(str)
			elif guiExists:
				logger.info(str)
				if logger.getEffectiveLevel() <= level:
					self.appendQtextcontent(u"<br>Info: %s" % (str))
			else:
				logger.info(str)
				if logger.getEffectiveLevel() <= level:
					msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information,
						title, u"Info: %s" % (str))
					msgBox.exec_()
		elif level == logging.WARN:
			if terminalMode:
				logger.warning(str)
			elif guiExists:
				logger.warning(str)
				if logger.getEffectiveLevel() <= level:
					self.appendQtextcontent(u"<br>Warning: %s" % (str))
			else:
				logger.warning(str)
				if logger.getEffectiveLevel() <= level:
					msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
						title, u"Warning: %s" % (str))
					msgBox.exec_()
		elif level == logging.ERROR:
			if terminalMode:
				logger.error(str)
			elif guiExists:
				logger.error(str)
				if logger.getEffectiveLevel() <= level:
					self.appendQtextcontent(u"<br>Error: %s" % (str))
			else:
				logger.error(str)
				if logger.getEffectiveLevel() <= level:
					msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
						title, u"Error: %s" % (str))
					msgBox.exec_()
		elif level == logging.CRITICAL:
			if terminalMode:
				logger.critical(str)
			elif guiExists:
				logger.critical(str)
				if logger.getEffectiveLevel() <= level:
					self.appendQtextcontent(u"<br>Critical: %s" % (str))
			else:
				logger.critical(str)
				if logger.getEffectiveLevel() <= level:
					msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
						title, u"Critical: %s" % (str))
					msgBox.exec_()
		if qtextbrowser is not None:
			# flush changes to GUI
			self.publishQtext()


class Settings(object):
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
		self.VArg = False
		self.HArg = False
		self.TArg = False
		self.LArg = basics.DEFAULTLOGLEVEL
		self.MArg = False
		self.NArg = False
		self.input = None
		self.output = None
		self.outputshort = None
		self.inputArgs = []  # list of input strings

		if logger is None:
			logging.basicConfig(stream=sys.stderr, level=basics.DEFAULTLOGLEVEL)
			self.logger = logging.getLogger(basics.LOGGERACRONYM)
		else:
			self.logger = logger

		if mlogger is None:
			self.mlogger = MLogger(terminalMode=None, logger=self.logger, qtextbrowser=None)
		else:
			self.mlogger = mlogger

	def printSettings(self):
		self.logger.debug("self.VArg = %s", self.VArg)
		self.logger.debug("self.HArg = %s", self.HArg)
		self.logger.debug("self.TArg = %s", self.TArg)
		self.logger.debug("self.LArg = %s", self.LArg)
		self.logger.debug("self.MArg = %s", self.MArg)
		self.logger.debug("self.NArg = %s", self.NArg)
		self.logger.debug("self.input = %s", self.input)
		self.logger.debug("self.outputshort = %s", self.outputshort)
		self.logger.debug("self.output = %s", u'***')
		self.logger.debug("self.inputArgs = %s", str(self.inputArgs))

	def gui2Settings(self, dialog):
		self.input = dialog.input()

	def settings2Gui(self, dialog):
		dialog.setInput(self.input)
		dialog.setOutput(self.outputshort)
		dialog.clipboard.setText(encoding.s2q(self.output))


class Args(object):
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
		self.settings = settings
		if logger is None:
			self.logger = settings.logger
		else:
			self.logger = logger

	def printVersion(self):
		print(u"Version: %s (%s)" % (basics.THVERSION, basics.THVERSIONTEXT))
		print(u"Python: %s" % sys.version.replace(" \n", "; "))

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

		Requires: python 2.7 or 3.4+ and PyQt4 and trezorlib library.
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
		# get defaults
		if logger is None:
			logger = self.logger
		if settings is None:
			settings = self.settings
		try:
			opts, args = getopt.getopt(argv, "vhl:tmn",
				["version", "help", "logging=", "terminal", "multiple", "noconfirm"])
		except getopt.GetoptError as e:
			msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, u"Wrong arguments",
				u"Error: %s" % e)
			msgBox.exec_()
			logger.critical(u'Wrong arguments. Error: %s.', e)
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

		if sys.version_info[0] > 2:
			settings.inputArgs = args
		else:
			for arg in args:
				# convert all input as possible to unicode UTF-8
				settings.inputArgs.append(arg.decode('utf-8'))
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
		self.settings.mlogger.log(u"Version: %s (%s)" %
			(basics.THVERSION, basics.THVERSIONTEXT),
			logging.INFO, "Wrong arguments", True, logger)
		self.settings.mlogger.log(u"Python: %s" % sys.version.replace(" \n", "; "),
			logging.INFO, "Wrong arguments", True, logger)
		self.settings.mlogger.log(u'Logging level set to %s (%d).' %
			(logging.getLevelName(settings.LArg), settings.LArg),
			logging.INFO, "Wrong arguments", True, logger)
		settings.printSettings()
