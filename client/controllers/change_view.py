import sys, socket, threading, queue, os
from threading import Thread, Event
from configparser import ConfigParser

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QStackedWidget, QButtonGroup, QAbstractButton
from client.views.login import Login
from client.views.logged import Logged
from client.views.connected import Connected
from client.widgets.main_window import Ui_MainWindow
from PyQt5.QtCore import pyqtSignal

main_program_is_over = Event()
callbacks = queue.Queue()
conversation_content = queue.Queue()


class MainView(QWidget, Ui_MainWindow):
    signal_login = pyqtSignal(str)
    signal_re = pyqtSignal(str)
    signal_away = pyqtSignal(str)
    signal_nick = pyqtSignal(str)
    signal_ask = pyqtSignal(str)
    signal_stop = pyqtSignal(str)
    signal_messages = pyqtSignal(str)
    signal_change_msg_accueil = pyqtSignal(str)

    def __configure(self, config_file):
        options = ConfigParser()
        options.read(config_file)

        if 'server' in options.sections():
            if 'ip' in options['server']:
                self.ip = options['server']['ip']
            if 'port' in options['server']:
                self.port = int(options["server"]["port"])

        return options

    def __persist_pseudo_at_login(self, pseudo):
        if not self.options["session"]:
            self.options["session"] = {}

        self.options["session"]["pseudo"] = pseudo

        with open("client.config", "w+") as config_file:
            self.options.write(config_file)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.ip = '127.0.0.1'
        self.port = 8123
        self.sock = None
        self.options = {}

        if os.path.exists('client.config'):
            self.options = self.__configure('client.config')

        self.conversation = conversation_content
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(20, 160, 621, 690))
        self.stackedWidget.setObjectName("stackedWidget")

        self.login_view = Login(self)
        self.login_view.signal_login.connect(self.send_request)
        self.login_view.signal_login.connect(lambda request, callback: self.__persist_pseudo_at_login(request.split()[-1]))
        self.stackedWidget.addWidget(self.login_view)
        self.signal_re.connect(self.handle_re)
        self.signal_away.connect(self.handle_away)
        self.signal_nick.connect(self.handle_nick)
        self.signal_ask.connect(self.handle_ask)
        self.signal_stop.connect(self.handle_stop)
        self.signal_change_msg_accueil.connect(lambda message: self.msg_accueil.setText(message))

        self.actionPasser_en_mode_actif.setEnabled(False)

        self.sub_lineEdit.hide()  # à mettre dans un widget pour tout cacher en meme temps
        self.sub_msg.hide()
        self.sub_button.hide()
        self.label_view = ""

        Thread(target=self.listen_in_background, args=(self.ip, self.port, self)).start()
        self.logged_view = Logged(self)
        self.logged_view.yes.hide()
        self.logged_view.no.hide()
        self.stackedWidget.addWidget(self.logged_view)
        self.connected_view = Connected(self)
        # handle mute buttons :
        self.connected_view.buttonGroup = QButtonGroup()
        self.connected_view.buttonGroup.buttonClicked[QAbstractButton].connect(self.connected_view.mute)
        # handle send file buttons :
        self.connected_view.filesGroup = QButtonGroup()
        self.connected_view.filesGroup.buttonClicked[QAbstractButton].connect(self.connected_view.send_file)

        self.stackedWidget.addWidget(self.connected_view)
        self.signal_messages.connect(self.logged_view.on_display)

        self.views = { 'login' : (0, self.login_view),  # index de la vue, vue
                       'logged' : (1, self.logged_view),
                       'connected' : (2, self.connected_view)
                       }

        self.current_user = ""
        timer = QTimer(self)
        timer.timeout.connect(self.update_label)
        timer.start(10000)

    def update(self, view):
        self.stackedWidget.setCurrentIndex(self.views[view][0])
        self.views[view][1].on_display()

    def update_label(self):
        self.msg_accueil.setText("Messagerie instantanée")

    @QtCore.pyqtSlot(str, object)
    def send_request(self, req, callback=None):
        global callbacks

        try:
            self.sock.send(req.encode())
            if callback:
                callbacks.put(callback)
        except KeyboardInterrupt:
            pass
        except:
            self.msg_accueil.setText("Impossible d'accéder au server,\n veuillez relancer le programme.")


    def listen_in_background(self, ip, port, view):
        global main_program_is_over, callbacks, conversation_content
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
                        self.signal_change_msg_accueil.emit("Connection avec le server perdue,\nveuillez relancer le programme")
                        main_program_is_over.set()  # si le serveur s'est arreté (envoyer plutot un signal d'erreur)
                        return
                    if not message.startswith(':'):
                        if callbacks.empty():
                            pass
                        else:
                            callback = callbacks.get()  # dat shit is bloquante
                            callback.emit(message)  # par exemple, appelle handle_response() de login
                    else:
                        conversation_content.put(message)  # fonction qui traite un message recu
                        self.signal_messages.emit("")
                    # print(message)
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
        new_pseudo = self.sub_lineEdit.text()
        self.sub_lineEdit.setText("")
        if not new_pseudo:
            self.sub_msg.setText("Merci de saisir un pseudo ! ")

        if self.label_view == "change_pseudo":
            self.send_request(f"NICK {new_pseudo}", self.signal_nick)
        if self.label_view == "msg_prive":
            self.send_request(f"ASK_WHISPER {new_pseudo}", self.signal_ask)
        if self.label_view == "delete_msg_prive":
            self.send_request(f"STOP_WHISPER {new_pseudo}", self.signal_stop)

    @QtCore.pyqtSlot(str)
    def handle_nick(self, server_response):
        if not server_response == '100 RPL_DONE':  # a changer
            self.sub_msg.setText("Ce pseudo est déjà pris... ")
        else:
            self.sub_lineEdit.hide()
            self.sub_msg.hide()
            self.sub_button.hide()
            self.msg_accueil.setText("Pseudo changé !")
            self.update('logged')

    @QtCore.pyqtSlot()  # se déconnecter
    def on_actionSe_d_connecter_triggered(self):
        self.send_request("QUIT")
        self.current_user = ""
        self.update('login')



    @QtCore.pyqtSlot()  # passer en mode actif
    def on_actionPasser_en_mode_actif_triggered(self):
        self.send_request("RE", self.signal_re)

    @QtCore.pyqtSlot(str)
    def handle_re(self, server_response):
        if not server_response == '100 RPL_DONE':  # a changer
            print("re not ok")
        else:
            print("re ok")
            self.actionPasser_en_mode_actif.setEnabled(False)
            self.actionPasser_en_mode_inactif.setEnabled(True)
            self.update('logged')

    @QtCore.pyqtSlot()  #passer en mode inactif
    def on_actionPasser_en_mode_inactif_triggered(self):
        self.send_request("AWAY", self.signal_away)

    @QtCore.pyqtSlot(str)
    def handle_away(self, server_response):
        if not server_response == '100 RPL_DONE':  # a changer
            print("away not ok")
        else:
            print("away ok")
            self.actionPasser_en_mode_actif.setEnabled(True)
            self.actionPasser_en_mode_inactif.setEnabled(False)
            self.update('logged')


    @QtCore.pyqtSlot()  # voir les membres connectés
    def on_actionVoir_les_membres_connect_s_triggered(self):
        self.update('connected')

    @QtCore.pyqtSlot()  # lancer une conversation privée
    def on_actionLancer_une_conversation_priv_e_triggered(self):
        self.sub_lineEdit.show()
        self.sub_msg.show()
        self.sub_msg.setText("Pseudo : ")
        self.sub_button.show()
        self.msg_accueil.setText("Lancer une conversation privée")
        self.label_view = "msg_prive"

    @QtCore.pyqtSlot(str)
    def handle_ask(self, server_response):
        if not server_response == '100 RPL_DONE':  # a changer
            self.sub_msg.setText("Une erreur est survenue... ")
        else:
            self.sub_lineEdit.hide()
            self.sub_msg.hide()
            self.sub_button.hide()
            self.msg_accueil.setText("Demande envoyée !")
            self.update('logged')

    @QtCore.pyqtSlot()  # lancer une conversation privée
    def on_actionSupprimer_une_conversation_priv_e_triggered(self):
        self.sub_lineEdit.show()
        self.sub_msg.show()
        self.sub_msg.setText("Pseudo : ")
        self.sub_button.show()
        self.msg_accueil.setText("Supprimer une conversation privée")
        self.label_view = "delete_msg_prive"

    @QtCore.pyqtSlot(str)
    def handle_stop(self, server_response):
        if not server_response == '100 RPL_DONE':  # a changer
            self.sub_msg.setText("Une erreur est survenue... ")
        else:
            self.sub_lineEdit.hide()
            self.sub_msg.hide()
            self.sub_button.hide()
            self.msg_accueil.setText("Conversation supprimée !")
            self.update('logged')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainView()
    win.show()
    ret = app.exec_()
    sys.exit(ret)