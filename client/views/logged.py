from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox

from projet.widgets.logged import Ui_Logged


class Logged(QWidget, Ui_Logged):
    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view
        print("in logged")

    @QtCore.pyqtSlot()
    def on_send_msg_clicked(self):
        pass