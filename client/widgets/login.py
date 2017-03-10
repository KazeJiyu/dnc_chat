# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Login.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(625, 841)
        self.msg_login = QtWidgets.QLabel(Login)
        self.msg_login.setGeometry(QtCore.QRect(0, 250, 621, 111))
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(14)
        self.msg_login.setFont(font)
        self.msg_login.setAlignment(QtCore.Qt.AlignCenter)
        self.msg_login.setObjectName("msg_login")
        self.login = QtWidgets.QLineEdit(Login)
        self.login.setGeometry(QtCore.QRect(100, 370, 431, 41))
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(12)
        self.login.setFont(font)
        self.login.setObjectName("login")
        self.submit_login = QtWidgets.QPushButton(Login)
        self.submit_login.setGeometry(QtCore.QRect(240, 450, 151, 41))
        self.submit_login.setObjectName("submit_login")

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        _translate = QtCore.QCoreApplication.translate
        Login.setWindowTitle(_translate("Login", "Form"))
        self.msg_login.setText(_translate("Login", "Bonjour ! Avec quel pseudo désirez-vous vous connecter ?"))
        self.submit_login.setText(_translate("Login", "Se connecter"))

