import sys
from PyQt5 import QtWidgets
from pythonlab.views.plotter import UserInterface


app = QtWidgets.QApplication(sys.argv)
ui = UserInterface()
ui.show()
sys.exit(app.exec())