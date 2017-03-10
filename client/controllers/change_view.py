import sys, socket, threading, queue
from threading import Thread, Event

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QLineEdit, QPushButton
from projet.views.login import Login
from projet.views.logged import Logged
from projet.views.connected import Connected
from projet.widgets.main_window import Ui_MainWindow

main_program_is_over = Event()
callbacks = queue.Queue()

class MainView(QWidget, Ui_MainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.child = Login(self)
        self.child.signal_login.connect(self.send_request)
        self.verticalLayoutWidget.layout().addWidget(self.child)
        self.sub_lineEdit.hide()  # à mettre dans un widget pour tout cacher en meme temps
        self.sub_msg.hide()
        self.sub_button.hide()
        self.label_view = ""
        self.ip = '127.0.0.1'
        self.port = 8123
        self.sock = None
        Thread(target=self.listen_in_background, args=(self.ip,self.port)).start()

    @QtCore.pyqtSlot(str, object)
    def send_request(self, req, callback):
        global callbacks

        try:
            self.sock.send(req.encode())
            callbacks.put(callback)
        except socket.gaierror:
            print(" [Error] Hostname could not be resolved")
        except socket.timeout:
            print(" [Error] Timeout: no response received from the server")
        except ConnectionResetError:
            print(" [Error] Unable to establish a connection")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(" [Error] " + str(e))

    def listen_in_background(self, ip, port):
        global main_program_is_over, callbacks
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.sock = sock
            self.sock.settimeout(3)
            try:
                sock.connect((ip, port))
            except ConnectionRefusedError:
                print("Server unreachable")  # qerrordialog + emettre un signal
                return
            while not main_program_is_over.is_set():
                try:
                    message = sock.recv(2048).decode()
                    if not message:
                        main_program_is_over.set()  # si le serveur s'est arreté (envoyer plutot un signal d'erreur)
                        return
                    if not message.startswith(':'):
                        callback = callbacks.get()
                        callback(message)  # par exemple, appelle handle_response() de login
                    else:
                        pass  # fonction qui traite un message recu
                    print(message)
                except socket.timeout:
                    pass
                except OSError:
                    return

    def closeEvent(self, event):
        print("Closing...") # faire un truc zoli
        main_program_is_over.set()

        for t in threading.enumerate():
            if t != threading.main_thread():
                t.join()
        event.accept()

    @QtCore.pyqtSlot()  # changer de pseudo
    def on_actionChanger_de_pseudo_triggered(self):
        self.sub_lineEdit.show()
        self.sub_msg.show()
        self.sub_msg.setText("Nouveau pseudo : ")
        self.sub_button.show()
        self.msg_accueil.setText("Changement de pseudo")
        self.label_view = "change_pseudo"

    @QtCore.pyqtSlot()
    def on_sub_button_clicked(self):
        if self.label_view == "change_pseudo":
            new_pseudo = self.sub_lineEdit.text()
            if not new_pseudo:
                self.sub_msg.setText("Merci de saisir un pseudo ! ")
            else:
                pseudo_taken = False  # en attendant l'interaction avec le serveur qui va bien
                if pseudo_taken:
                    self.sub_msg.setText("Ce pseudo est déjà pris... ")
                else:
                    self.sub_lineEdit.hide()
                    self.sub_msg.hide()
                    self.sub_button.hide()
                    self.msg_accueil.setText("Pseudo changé !")

        if self.label_view == "msg_prive":
            pass

    @QtCore.pyqtSlot()  # se déconnecter
    def on_actionSe_d_connecter_triggered(self):
        # self.update("log_out")
        pass

    @QtCore.pyqtSlot()  # passer en mode actif
    def on_actionPasser_en_mode_actif_triggered(self):
        # self.update("get_active")
        pass

    @QtCore.pyqtSlot()  #passer en mode inactif
    def on_actionPasser_en_mode_inactif_triggered(self):
        # self.update("get_inactive")
        pass

    @QtCore.pyqtSlot()  # voir les membres connectés
    def on_actionVoir_les_membres_connect_s_triggered(self):
        self.update("see_logged")
        # pass

    @QtCore.pyqtSlot()  # lancer une conversation privée
    def on_actionLancer_une_conversation_priv_e_triggered(self):
        self.sub_lineEdit.show()
        self.sub_msg.show()
        self.sub_msg.setText("Pseudo : ")
        self.sub_button.show()
        self.msg_accueil.setText("Lancer une conversation privée")
        self.label_view = "msg_prive"

    def update(self, view, param=None):  # use a dict for the menu
        self.verticalLayoutWidget.layout().removeWidget(self.child)
        self.child.deleteLater()
        print("in update")
        if view == "logged":
            self.child = Logged(self)
            print("supposed to add a widget")
        elif view == "change_pseudo":
            pass
        elif view == "log_out":
            pass
        elif view == "get_active":
            pass
        elif view == "get_inacive":
            pass
        elif view == "see_logged":
            self.child = Connected(self)
        elif view == "start_private_conversation":
            pass

        self.verticalLayoutWidget.layout().addWidget(self.child)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainView()
    win.show()
    ret = app.exec_()
    sys.exit(ret)