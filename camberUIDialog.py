# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camberUIDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

# PyInstaller command: pyinstaller -F camberUIDialog.py -n -w "Camber Disc Golf Background Removal Tool" --icon=camberShirtLogo.png  --add-data "u2net.onnx;." --add-data "camberShirtLogo.png;."


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(513, 214)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("camberShirtLogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.inputFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.inputFileButton.setGeometry(QtCore.QRect(400, 20, 91, 31))
        self.inputFileButton.setObjectName("inputFileButton")
        self.outputSelection = QtWidgets.QLineEdit(self.centralwidget)
        self.outputSelection.setGeometry(QtCore.QRect(100, 71, 261, 31))
        self.outputSelection.setObjectName("outputSelection")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 150, 351, 31))
        self.progressBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(True)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.inputSelection = QtWidgets.QLineEdit(self.centralwidget)
        self.inputSelection.setGeometry(QtCore.QRect(100, 20, 261, 31))
        self.inputSelection.setObjectName("inputSelection")
        self.outputDirButton = QtWidgets.QPushButton(self.centralwidget)
        self.outputDirButton.setGeometry(QtCore.QRect(400, 71, 91, 31))
        self.outputDirButton.setObjectName("outputDirButton")
        self.outputFileLabel = QtWidgets.QLabel(self.centralwidget)
        self.outputFileLabel.setGeometry(QtCore.QRect(10, 70, 81, 31))
        self.outputFileLabel.setObjectName("outputFileLabel")
        self.inputFileLabel = QtWidgets.QLabel(self.centralwidget)
        self.inputFileLabel.setGeometry(QtCore.QRect(10, 19, 51, 31))
        self.inputFileLabel.setObjectName("inputFileLabel")
        self.executeButton = QtWidgets.QPushButton(self.centralwidget)
        self.executeButton.setGeometry(QtCore.QRect(400, 150, 91, 31))
        self.executeButton.setObjectName("executeButton")
        self.mainLabel = QtWidgets.QLabel(self.centralwidget)
        self.mainLabel.setGeometry(QtCore.QRect(20, 190, 61, 16))
        self.mainLabel.setText("")
        self.mainLabel.setObjectName("mainLabel")
        self.transparentCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.transparentCheckbox.setGeometry(QtCore.QRect(9, 116, 191, 20))
        self.transparentCheckbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.transparentCheckbox.setObjectName("transparentCheckbox")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Camber Disc Golf Background Removal Tool"))
        self.inputFileButton.setText(_translate("MainWindow", "Select"))
        self.outputDirButton.setText(_translate("MainWindow", "Select"))
        self.outputFileLabel.setText(_translate("MainWindow", "Output Directory"))
        self.inputFileLabel.setText(_translate("MainWindow", "Input Files"))
        self.executeButton.setText(_translate("MainWindow", "Execute"))
        self.transparentCheckbox.setText(_translate("MainWindow", "Transparent backgrounds included?"))
