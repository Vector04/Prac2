from PyQt5 import QtWidgets, uic
import sys

class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load ui
        uic.loadUi(open("first_design.ui"), self)

        # Button functions
        self.clear_button.clicked.connect(self.textedit.clear)
        self.add_button.clicked.connect(self.add_button_clicked)

    def add_button_clicked(self):
        self.textedit.append("You clicked me.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())