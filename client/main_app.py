import sys
import os

# let python know other modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from client.controllers.change_view import MainView

#fichier principal, à exécuter
class App():
    def __init__(self):
        self.view = MainView()
        self.view.show()

def my_excepthook(type, value, tback):
    sys.__excepthook__(type, value, tback)

if __name__ == '__main__':
    sys.excepthook = my_excepthook

    app = QApplication(sys.argv)
    win = App()
    ret = app.exec_()
    sys.exit(ret)