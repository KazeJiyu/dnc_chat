# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Connected.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Connected(object):
    def setupUi(self, Connected):
        Connected.setObjectName("Connected")
        Connected.resize(625, 723)
        self.connected_ppl = QtWidgets.QListView(Connected)
        self.connected_ppl.setGeometry(QtCore.QRect(20, 20, 581, 601))
        self.connected_ppl.setObjectName("connected_ppl")
        self.pushButton = QtWidgets.QPushButton(Connected)
        self.pushButton.setGeometry(QtCore.QRect(210, 650, 201, 34))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Connected)
        QtCore.QMetaObject.connectSlotsByName(Connected)

    def retranslateUi(self, Connected):
        _translate = QtCore.QCoreApplication.translate
        Connected.setWindowTitle(_translate("Connected", "Form"))
        self.pushButton.setText(_translate("Connected", "Retour à la conversation"))

