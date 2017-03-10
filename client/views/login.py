from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from projet.widgets.login import Ui_Login


class Login(QWidget, Ui_Login):
    signal_login = pyqtSignal(str, object)

    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view
        self.view.menuMon_compte.setEnabled(False)
        self.view.menuConversation.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_submit_login_clicked(self):
        pseudo = self.login.text()
        if not pseudo:
            self.msg_login.setText("Merci de saisir un pseudo ! ")
        else:
            self.signal_login.emit(f"CONNECT {pseudo}", self.handle_response)
            # print("ya connected")
            # self.view.menuMon_compte.setEnabled(True)
            # self.view.menuConversation.setEnabled(True)
            # self.view.update("logged")

    def handle_response(self, server_response):
        if not server_response == '100 RPL_DONE':
            self.msg_login.setText("Ce pseudo est déjà pris... ")
        else:
            print("ya connected")
            self.view.menuMon_compte.setEnabled(True)
            self.view.menuConversation.setEnabled(True)
            self.view.update("logged")
