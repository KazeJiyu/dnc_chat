from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from client.widgets.login import Ui_Login


class Login(QWidget, Ui_Login):
    signal_login = pyqtSignal(str, object)  # document all signals
    signal_handle_response = pyqtSignal(str)

    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view
        self.view.menuMon_compte.setEnabled(False)
        self.view.menuConversation.setEnabled(False)
        self.signal_handle_response.connect(self.handle_response)
        self.login.returnPressed.connect(self.on_submit_login_clicked)

    def on_display(self):
        pass

    @QtCore.pyqtSlot()
    def on_submit_login_clicked(self):
        pseudo = self.login.text()
        if not pseudo:
            self.msg_login.setText("Merci de saisir un pseudo ! ")
        else:
            self.signal_login.emit(f"CONNECT {pseudo}", self.signal_handle_response)
            self.view.menuMon_compte.setEnabled(True)
            self.view.menuConversation.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def handle_response(self, server_response):
        if not server_response == '100 RPL_DONE':
            self.login.setText("")
            self.msg_login.setText("Ce pseudo est déjà pris... ")
        else:
            self.view.menuMon_compte.setEnabled(True)
            self.view.menuConversation.setEnabled(True)
            self.view.current_user = self.login.text()
            self.login.setText("")
            print(f"current user : {self.view.current_user}")
            self.view.update("logged")
