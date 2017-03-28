import os
from os.path import basename, splitext
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QPushButton, QFileDialog

from client.widgets.connected import Ui_Connected


class Connected(QWidget, Ui_Connected):
    signal_connected = pyqtSignal(str, object)  # document all signals
    signal_handle_response = pyqtSignal(str)
    signal_handle_mute = pyqtSignal(str)
    signal_handle_listen = pyqtSignal(str)
    signal_handle_file = pyqtSignal(str)

    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view
        self.signal_connected.connect(self.view.send_request)
        self.signal_handle_response.connect(self.handle_response)
        self.signal_handle_mute.connect(self.handle_mute)
        self.signal_handle_listen.connect(self.handle_listen)
        self.signal_handle_file.connect(self.handle_file)
        self.last_btn_clicked = None
        self.mute_ppl = []


    def on_display(self):
        self.signal_connected.emit("NAMES", self.signal_handle_response)

    @QtCore.pyqtSlot(str)
    def handle_response(self, server_response):
        self.connected_ppl.clear()
        self.list_buttons.clear()
        if not server_response.startswith('101 RPL_NAMES'):
            self.view.msg_accueil.setText("Une erreur est survenue... ")
        else:
            for i in server_response.split()[2:]:
                if i != self.view.current_user:
                    # mute button :
                    if i not in self.mute_ppl :
                        button = QPushButton("mute")
                    else:
                        button = QPushButton("unmute")
                    button.setObjectName(f"{i}")
                    self.buttonGroup.addButton(button)
                    item = QListWidgetItem(self.list_buttons)
                    self.list_buttons.setItemWidget(item, button)
                    # send file button :
                    btn_file = QPushButton("send file")
                    btn_file.setObjectName(f"f_{i}")
                    self.filesGroup.addButton(btn_file)
                    item_file = QListWidgetItem(self.list_files)
                    self.list_files.setItemWidget(item_file, btn_file)
                    # name of the user:
                    name = QListWidgetItem(i)
                    self.connected_ppl.addItem(name)

    @QtCore.pyqtSlot(str)
    def handle_mute(self, server_response):
        if not server_response.startswith('100 RPL_DONE'):
            self.view.msg_accueil.setText("Une erreur est survenue... ")
        else:
            self.mute_ppl.append(self.last_btn_clicked.objectName())
            self.last_btn_clicked.setText("unmute")
            self.last_btn_clicked = None


    @QtCore.pyqtSlot(str)
    def handle_listen(self, server_response):
        if not server_response.startswith('100 RPL_DONE'):
            self.view.msg_accueil.setText("Une erreur est survenue... ")
        else:
            self.mute_ppl.remove(self.last_btn_clicked.objectName())
            self.last_btn_clicked.setText("mute")
            self.last_btn_clicked = None


    def mute(self, button):
        self.last_btn_clicked = button
        if button.text() == "mute":
            self.signal_connected.emit(f"MUTE {button.objectName()}", self.signal_handle_mute)
        else:
            self.signal_connected.emit(f"LISTEN {button.objectName()}", self.signal_handle_listen)

    def send_file(self, button):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                filename =basename(f.name)
                print(f" filename : {filename}")
                # data = f.read()
                statinfo = os.stat(f'{f.name}')
                print(f"size of data to {button.objectName()[2:]}: {statinfo.st_size}")
                self.signal_connected.emit(f"ASK_FILE {button.objectName()[2:]} {statinfo.st_size} {filename}", self.signal_handle_file)

    @QtCore.pyqtSlot(str)
    def handle_file(self, server_response):
        if not server_response.startswith('102 RPL_FILE'):
            self.view.msg_accueil.setText("Une erreur est survenue... ")
        else:
            self.view.msg_accueil.setText("Requête envoyée ! ")
            self.view.logged_view.my_file_requests.append(server_response.split()[2])
            self.view.update('logged')

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.view.update("logged")