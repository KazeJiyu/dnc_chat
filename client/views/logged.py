from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QPushButton

from client.widgets.logged import Ui_Logged

def cmd_message(view, sender, content):
    return QListWidgetItem(f"[{sender}] {content}")

def cmd_nick(view, sender, content):
    return QListWidgetItem(f"{sender} a changé son pseudo en {content}.")

def cmd_connect(view, sender, content):
    return QListWidgetItem(f"{sender} vient de se connecter !")

def cmd_quit(view, sender, content):
    return QListWidgetItem(f"{sender} vient de quitter la conversation.")

def cmd_ask_whisper(view, sender, content):
    print("in cmd_ask_whisper")
    accepter = QPushButton("Accepter")
    ignorer = QPushButton("Ignorer")
    accepter.clicked.connect(lambda: view.signal_handle_whisper.emit("YES", sender))
    ignorer.clicked.connect(lambda: view.signal_handle_whisper.emit("NO", sender))
    message = f"{sender} désire lancer une conversation privée. Acceptez-vous ?"
    return QListWidgetItem(message)

def cmd_reply_whisper(view, sender, content):
    print("in cmd_reply_whisper")
    if content == "YES":
        view.private_conversations.append(sender)
        return QListWidgetItem(f"{sender} a accepté votre demande de conversation privée !")
    return QListWidgetItem(f"{sender} a refusé votre demande de conversation privée.")

def cmd_whisper(view, sender, content):
    item = QListWidgetItem(f"[Message privé de {sender}] {content}")
    item.setFont(QtGui.QFont('Tahoma', 8, QtGui.QFont.Bold))
    return item

def cmd_stop_whisper(view, sender, content):
    return QListWidgetItem(f"{sender} a mis fin à votre conversation privée.")

def cmd_ask_file(view, sender, content):
    accepter = QPushButton("Accepter")
    ignorer = QPushButton("Ignorer")
    accepter.clicked.connect(lambda: view.signal_handle_file.emit("YES", sender, content.split()[0]))
    ignorer.clicked.connect(lambda: view.signal_handle_file.emit("NO", content.split()[0]))
    message = f"{sender} désire vous envoyer un fichier nommé {content.split()[2]} de {content.split()[1]} bytes. " \
           f"Acceptez-vous ?"
    return QListWidgetItem(message)


class Logged(QWidget, Ui_Logged):
    signal_msg = pyqtSignal(str, object)  # document all signals
    signal_handle_response = pyqtSignal(str)
    signal_handle_whisper = pyqtSignal(str, str)  # yes/no, sender
    signal_handle_file = pyqtSignal(str, str)  # yes/no, request id

    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.view = view
        self.view.msg_accueil.setText("Messagerie instantanée")
        self.signal_msg.connect(self.view.send_request)
        self.signal_handle_response.connect(self.handle_response)
        self.signal_handle_whisper.connect(self.handle_whisper)
        self.signal_handle_file.connect(self.handle_file)
        self.private_conversations = []
        self.my_file_requests = []
        self.commands = {
            "MESSAGE": cmd_message,
            "NICK": cmd_nick,
            "CONNECT": cmd_connect,
            "QUIT": cmd_quit,
            "ASK_WHISPER": cmd_ask_whisper,
            "REPLY_WHISPER": cmd_reply_whisper,
            "WHISPER": cmd_whisper,
            "STOP_WHISPER": cmd_stop_whisper,
            "ASK_FILE": cmd_ask_file
        }


    def on_display(self):
        self.messages = self.view.conversation

        if not self.messages.empty():
            new_msg = self.messages.get()
            print(new_msg)
            if new_msg.startswith(':'):
                sender = ''.join(new_msg.split()[:1]).lstrip(':')
                content = ' '.join(new_msg.split()[2:])
                item = self.commands[new_msg.split()[1]](self, sender, content)
            else:
                if not self.view.actionPasser_en_mode_actif.isEnabled():
                    item = QListWidgetItem(f"Moi : {new_msg}")
                else:
                    return

            self.conversation.addItem(item)


    @QtCore.pyqtSlot()
    def handle_whisper(self, reply, sender):
        self.signal_msg.emit(f"REPLY_WHISPER {sender} {reply}", self.signal_handle_response)

    def handle_file(self, reply, request_id):
        if reply == "YES":
            port = 8432  # open a udp connection
            self.signal_msg.emit(f"REPLY_FILE {request_id} {reply} {port}", self.signal_handle_response)
        else:
            self.signal_msg.emit(f"REPLY_FILE {request_id} {reply}", self.signal_handle_response)

    @QtCore.pyqtSlot()
    def on_send_msg_clicked(self):
        msg_content = self.msg.toPlainText()
        self.msg.clear()
        self.view.conversation.put(msg_content)
        self.on_display()
        if not msg_content.startswith('@'):
            self.signal_msg.emit(f"MESSAGE {msg_content}", self.signal_handle_response)
        else:
            self.signal_msg.emit(f"WHISPER {msg_content.split()[0][1:]} {' '.join(msg_content.split()[1:])}", self.signal_handle_response)


    @QtCore.pyqtSlot(str)
    def handle_response(self, server_response):
        if not server_response == '100 RPL_DONE':  # traiter les cas de whisper impossible...
            self.view.msg_accueil.setText("Une erreur est survenue... ")
