import sys

from PyQt5 import QtWidgets


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # roep de __init__() aan van de parent class
        super().__init__()

        # elk QMainWindow moet een central widget hebben
        # hierbinnen maak je een layout en hang je andere widgets
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # voeg geneste layouts en widgets toe
        vbox = QtWidgets.QVBoxLayout(central_widget)
        self.textedit = QtWidgets.QTextEdit()
        vbox.addWidget(self.textedit)
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        clear_button = QtWidgets.QPushButton("Clear")
        hbox.addWidget(clear_button)
        add_button = QtWidgets.QPushButton("Add text")
        hbox.addWidget(add_button)

        # Slots and signals
        clear_button.clicked.connect(self.textedit.clear)
        add_button.clicked.connect(self.add_button_clicked)


        # Adding two more buttons
        hbox2 = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox2)

        hworld = QtWidgets.QPushButton("Hello, World!")
        hbox2.addWidget(hworld)
        hworld.clicked.connect(self.hworld_button_clicked)

        closebutton = QtWidgets.QPushButton("Quit")
        hbox2.addWidget(closebutton)
        closebutton.clicked.connect(self.close)




    def add_button_clicked(self):
        self.textedit.append("You clicked me.")

    def hworld_button_clicked(self):
        self.textedit.append("Hello, World!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())
