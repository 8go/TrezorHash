from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from PyQt4 import QtGui
from PyQt4.QtGui import QPixmap

from ui_dialog import Ui_Dialog

from encoding import q2s, s2q
from processing import processAll

import basics


class Dialog(QtGui.QDialog, Ui_Dialog):

	DESCRHEADER = """<!DOCTYPE html><html><head>
		<body style="font-size:11pt; font-weight:400; font-style:normal;">
		<b>Welcome to TrezorHash</b>, version """ + basics.THVERSION + """ from
		""" + basics.THVERSIONTEXT + """<br>The output, the encrypted hash, is
		placed on the clipboard. The only way to get it is by pasting it to
		your destination.
		"""
	DESCRTRAILER = "</p></body></html>"

	def __init__(self, trezor, settings):
		QtGui.QDialog.__init__(self)
		self.setupUi(self)

		self.trezor = trezor
		self.settings = settings
		self.teh = None

		self.inputField.textChanged.connect(self.validate)
		self.validate()
		self.version = ""
		self.description1 = self.DESCRHEADER
		self.description2 = ""
		self.description3 = self.DESCRTRAILER

		# Apply is not automatically set up, only OK is automatically set up
		button = self.buttonBox.button(QtGui.QDialogButtonBox.Apply)  # QtGui.QDialogButtonBox.Ok
		button.clicked.connect(self.accept)
		# Abort is automatically set up as Reject, like Cancel

		# self.buttonBox.clicked.connect(self.handleButtonClick)  # connects ALL buttons
		# Created the action in GUI with designer-qt4
		self.actionApply.triggered.connect(self.accept)  # Save
		self.actionDone.triggered.connect(self.reject)  # Quit
		QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.reject)  # Quit
		QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self.accept)  # Save
		QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self, self.accept)  # Apply
		QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self, self.copy2Clipboard)
		QtGui.QShortcut(QtGui.QKeySequence("Ctrl+T"), self, self.printAbout)  # Version/About

		self.clipboard = QtGui.QApplication.clipboard()
		self.textBrowser.selectionChanged.connect(self.selectionChanged)

	def descrHeader(self):
		return self.DESCRHEADER

	def descrContent(self):
		return self.description2

	def descrTrailer(self):
		return self.DESCRTRAILER

	def printAbout(self):
		"""
		Show window with about and version information.
		"""
		msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information, "About",
			"About <b>TrezorHash</b>: <br><br>TrezorHash " +
			"computes the encrypted hash (digest) of an input string "
			"(message) using a Trezor hardware "
			"device for safety and security.<br><br>" +
			"<b>Version: </b>" + basics.THVERSION +
			" from " + basics.THVERSIONTEXT)
		msgBox.setIconPixmap(QPixmap("icons/TrezorHash.92x128.png"))
		msgBox.exec_()

	def selectionChanged(self):
		"""
		called whenever selected text in textarea is changed
		"""
		# self.textBrowser.copy()  # copy selected to clipboard
		# self.settings.mlogger.log("Copied text to clipboard: %s" % self.clipboard.text(),
		# 	logging.DEBUG, "Clipboard")
		pass

	def copy2Clipboard(self):
		self.textBrowser.copy()  # copy selected to clipboard
		# This is content from the Status textarea, so no secrets here, we can log it
		self.settings.mlogger.log("Copied text to clipboard: %s" % self.clipboard.text(),
			logging.DEBUG, "Clipboard")

	def setTeh(self, teh):
		self.teh = teh

	def setVersion(self, version):
		self.version = version

	def setDescription(self, extradescription):
		self.textBrowser.setHtml(s2q(self.description1 + extradescription + self.description3))

	def appendDescription(self, extradescription):
		"""
		@param extradescription: text in HTML format, use </br> for linebreaks
		"""
		self.description2 += extradescription
		self.textBrowser.setHtml(s2q(self.description1 + self.description2 + self.description3))

	def input(self):
		return q2s(self.inputField.text())

	def setInput(self, arg):
		self.inputField.setText(s2q(arg))

	def output(self):
		return q2s(self.outputField.text())

	def setOutput(self, arg):
		self.outputField.setText(s2q(arg))

	def validate(self):
		"""
		Enable OK/Apply buttons only if both master and backup are repeated
		without typo and some file is selected and
		exactly a single decrypt/encrypt option from the radio buttons is set.
		And only when Encrypt is selected.
		On decrypt passphrase does not need to be specified twice.
		"""
		# QtGui.QDialogButtonBox.Ok
		button = self.buttonBox.button(QtGui.QDialogButtonBox.Apply)
		button.setEnabled((self.input() != ""))
		return (self.input() != "")

	# def handleButtonClick(self, button):
		# sb = self.buttonBox.standardButton(button)
		# if sb == QtGui.QDialogButtonBox.Apply:
		# 	processAll(self.trezor, self.settings, self)
		# # elif sb == QtGui.QDialogButtonBox.Reset:
		# #	self.settings.mlogger.log("Reset Clicked, quitting now...", logging.DEBUG, "UI")

	def accept(self):
		"""
		Apply button was pressed
		"""
		if self.validate():
			self.settings.mlogger.log("Apply was called by user request. Start processing now.",
				logging.DEBUG, "GUI IO")
			processAll(self.teh, self.settings, self)  #
		else:
			self.settings.mlogger.log("Apply was called by user request. Apply is denied. "
				"User input is not valid for processing. Did you enter an input string?",
				logging.DEBUG, "GUI IO")

	# Don't set up a reject() method, it is automatically created.
	# If created here again it would overwrite the default one
	# def reject(self):
	# 	self.close()
