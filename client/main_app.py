import sys

from PyQt5.QtWidgets import QApplication
from projet.controllers.change_view import MainView

#fichier principal, à exécuter
class App():
    def __init__(self):
        self.view = MainView()
        self.view.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = App()
    ret = app.exec_()
    sys.exit(ret)