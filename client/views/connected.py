from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget

from projet.widgets.connected import Ui_Connected


class Connected(QWidget, Ui_Connected):
    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.view.update("logged")