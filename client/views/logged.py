from socket import *
import threading
from threading import Thread, Event
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout, QLayout, QFileDialog

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
    
    # create a new widget to display the message and the buttons at once
    widgetLayout = QHBoxLayout()
    widgetLayout.addWidget(QLabel(message))
    widgetLayout.addWidget(accepter)
    widgetLayout.addWidget(ignorer)
    widgetLayout.addStretch()
    widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
    
    widget = QWidget()
    widget.setLayout(widgetLayout)  
    
    item = QListWidgetItem()
    item.setSizeHint(widget.sizeHint())    

    return item, widget

def cmd_reply_whisper(view, sender, content):
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
    accepter.clicked.connect(lambda: view.signal_handle_file.emit("YES", content.split()[0]))
    ignorer.clicked.connect(lambda: view.signal_handle_file.emit("NO", content.split()[0]))
    message = f"{sender} désire vous envoyer un fichier nommé {content.split()[2]} de {content.split()[1]} bytes. " \
           f"Acceptez-vous ?"
    view.my_file_requests[content.split()[0]] = (content.split()[2],content.split()[1])

    # create a new widget to display the message and the buttons at once
    widgetLayout = QHBoxLayout()
    widgetLayout.addWidget(QLabel(message))
    widgetLayout.addWidget(accepter)
    widgetLayout.addWidget(ignorer)
    widgetLayout.addStretch()
    widgetLayout.setSizeConstraint(QLayout.SetFixedSize)

    widget = QWidget()
    widget.setLayout(widgetLayout)

    item = QListWidgetItem()
    item.setSizeHint(widget.sizeHint())
    return item, widget

def cmd_reply_file(view, sender, content):
    if content.split()[1].lower() == "yes":
        port = content.split()[2]
        ip = content.split()[3]
        
        # send the file
        filename = view.my_file_requests[content.split()[0]][0]
        file_size = view.my_file_requests[content.split()[0]][1]
        
        amount_read = 0
        
        with open(filename, 'rb') as f:
            while True and amount_read < file_size:
                data = f.read(1048)
                
                amount_read += 1048
                
                with socket(AF_INET, SOCK_DGRAM) as sock:
                    sock.sendto(data, (ip, int(port)))
                    
        return QListWidgetItem(f"{sender} a accepté votre demande d'envoi de fichier !")
    return QListWidgetItem(f"{sender} a refusé votre demande d'envoi de fichier.")


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
        self.my_file_requests = {}
        self.commands = {
            "MESSAGE": cmd_message,
            "NICK": cmd_nick,
            "CONNECT": cmd_connect,
            "QUIT": cmd_quit,
            "ASK_WHISPER": cmd_ask_whisper,
            "REPLY_WHISPER": cmd_reply_whisper,
            "WHISPER": cmd_whisper,
            "STOP_WHISPER": cmd_stop_whisper,
            "ASK_FILE": cmd_ask_file,
            "REPLY_FILE": cmd_reply_file
        }


    def on_display(self):
        self.messages = self.view.conversation

        if not self.messages.empty():
            new_msg = self.messages.get()
            widget = None
            print(new_msg)
            if new_msg.startswith(':'):
                sender = ''.join(new_msg.split()[:1]).lstrip(':')
                content = ' '.join(new_msg.split()[2:])
                if sender not in self.view.connected_view.mute_ppl:
                    item = self.commands[new_msg.split()[1]](self, sender, content)
                else:
                    return
            else:
                if not self.view.actionPasser_en_mode_actif.isEnabled():
                    item = QListWidgetItem(f"Moi : {new_msg}")
                else:
                    return

            if isinstance(item, tuple):
                self.conversation.addItem(item[0])
                self.conversation.setItemWidget(item[0], item[1])
            else:
                self.conversation.addItem(item)

    @QtCore.pyqtSlot(str, str)
    def handle_whisper(self, reply, sender):
        self.signal_msg.emit(f"REPLY_WHISPER {sender} {reply}", self.signal_handle_response)

    @QtCore.pyqtSlot(str, str)
    def handle_file(self, reply, request_id):
        if reply == "YES":
            port = 8432  # open a udp connection

            name = QFileDialog.getSaveFileName(self, 'Save File')
            Thread(target=self.receive_files, args=(name[0], request_id, port)).start()
            self.signal_msg.emit(f"REPLY_FILE {request_id} {reply} {port}", self.signal_handle_response)
        else:
            self.signal_msg.emit(f"REPLY_FILE {request_id} {reply}", self.signal_handle_response)

    def receive_files(self, new_file_name, request_id, port):
        file_size = self.my_file_requests[request_id][1]
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind(('', port))
            print(f"socket bound")
            amount_received = 0
            
            while True and amount_received < int(file_size):
                requete = sock.recvfrom(1048)
                amount_received += 1048
                
                if not requete:
                    break;
                
                (mess, adr_client) = requete

                with open(new_file_name, 'ab') as file:
                    file.write(mess)
                    
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
