from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PyQt4 import QtGui, QtCore

from ui_trezor_passphrase_dialog import Ui_TrezorPassphraseDialog
from ui_enter_pin_dialog import Ui_EnterPinDialog
from ui_trezor_chooser_dialog import Ui_TrezorChooserDialog

from encoding import q2s


class TrezorPassphraseDialog(QtGui.QDialog, Ui_TrezorPassphraseDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.setupUi(self)

	def passphrase(self):
		return q2s(self.passphraseEdit.text())


class EnterPinDialog(QtGui.QDialog, Ui_EnterPinDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.setupUi(self)

		self.pb1.clicked.connect(self.pinpadPressed)
		self.pb2.clicked.connect(self.pinpadPressed)
		self.pb3.clicked.connect(self.pinpadPressed)
		self.pb4.clicked.connect(self.pinpadPressed)
		self.pb5.clicked.connect(self.pinpadPressed)
		self.pb6.clicked.connect(self.pinpadPressed)
		self.pb7.clicked.connect(self.pinpadPressed)
		self.pb8.clicked.connect(self.pinpadPressed)
		self.pb9.clicked.connect(self.pinpadPressed)

	def pin(self):
		return q2s(self.pinEdit.text())

	def pinpadPressed(self):
		sender = self.sender()
		objName = sender.objectName()
		digit = objName[-1]
		self.pinEdit.setText(self.pinEdit.text() + digit)


class TrezorChooserDialog(QtGui.QDialog, Ui_TrezorChooserDialog):

	def __init__(self, deviceMap):
		"""
		Create dialog and fill it with labels from deviceMap

		@param deviceMap: dict device string -> device label
		"""
		QtGui.QDialog.__init__(self)
		self.setupUi(self)

		for deviceStr, label in deviceMap.items():
			item = QtGui.QListWidgetItem(label)
			item.setData(QtCore.Qt.UserRole, QtCore.QVariant(deviceStr))
			self.trezorList.addItem(item)
		self.trezorList.setCurrentRow(0)

	def chosenDeviceStr(self):
		"""
		Returns device string of chosen Trezor
		"""
		itemData = self.trezorList.currentItem().data(QtCore.Qt.UserRole)
		deviceStr = str(itemData.toString())
		return deviceStr
