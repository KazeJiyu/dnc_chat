# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Logged.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Logged(object):
    def setupUi(self, Logged):
        Logged.setObjectName("Logged")
        Logged.resize(625, 723)
        self.conversation = QtWidgets.QListWidget(Logged)
        self.conversation.setGeometry(QtCore.QRect(20, 20, 581, 451))
        self.conversation.setObjectName("conversation")
        self.msg = QtWidgets.QTextEdit(Logged)
        self.msg.setGeometry(QtCore.QRect(20, 520, 581, 121))
        self.msg.setObjectName("msg")
        self.label = QtWidgets.QLabel(Logged)
        self.label.setGeometry(QtCore.QRect(0, 490, 171, 19))
        self.label.setObjectName("label")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Logged)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 650, 581, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.layout_send = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.layout_send.setContentsMargins(0, 0, 0, 0)
        self.layout_send.setObjectName("layout_send")
        self.send_msg = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.send_msg.setObjectName("send_msg")
        self.layout_send.addWidget(self.send_msg)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(Logged)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(154, 480, 451, 36))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.layout_yes_no = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.layout_yes_no.setContentsMargins(0, 0, 0, 0)
        self.layout_yes_no.setObjectName("layout_yes_no")
        self.yes = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.yes.setObjectName("yes")
        self.layout_yes_no.addWidget(self.yes)
        self.no = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.no.setObjectName("no")
        self.layout_yes_no.addWidget(self.no)

        self.retranslateUi(Logged)
        QtCore.QMetaObject.connectSlotsByName(Logged)

    def retranslateUi(self, Logged):
        _translate = QtCore.QCoreApplication.translate
        Logged.setWindowTitle(_translate("Logged", "Form"))
        self.msg.setHtml(_translate("Logged", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label.setText(_translate("Logged", "Tapez un message..."))
        self.send_msg.setText(_translate("Logged", "Envoyer"))
        self.yes.setText(_translate("Logged", "Oui"))
        self.no.setText(_translate("Logged", "Non"))

