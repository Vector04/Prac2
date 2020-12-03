import sys

from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
import numpy as np
import pkg_resources

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

def inverse(x):
    try:
        return 1/x
    except ZeroDivisionError:
        return 0


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        # Load ui
        # uic.loadUi(open("plotter.ui"), self)

        uic.loadUi(pkg_resources.resource_stream("pythonlab.views", "plotter.ui"), self)

        
        # Sliders
        self.startslider.valueChanged.connect(self.update_plot)
        self.endslider.valueChanged.connect(self.update_plot)
        self.numpointsslider.valueChanged.connect(self.update_plot)

        # Combobox
        # self.funcselect.addItems(['sin', 'cos', 'tan', 'exp', 'x', 'x^2', 'x^3', '1/x'])
        # self.funcdict = {'sin':np.sin, 'cos':np.cos, 'tan':np.tan, 'exp':np.exp,
        #     'x': lambda x: x, 'x^2': lambda x: x**2, 'x^3': lambda x: x**3, '1/x':inverse}
        # self.funcselect.currentTextChanged.connect(self.update_plot)

        # Function editor
        self.funcedit.returnPressed.connect(self.update_plot)


        xs = np.linspace(-np.pi, np.pi, 50)
        self.plotwidget.plot(xs, np.sin(xs), pen={"color": "g","width": 3})

        self.plotwidget.setLabel("left", "f(x)")
        self.plotwidget.setLabel("bottom", "x")


       
    def update_plot(self):
        # New plot data
        start = self.startslider.value()
        end = self.endslider.value()
        numpoints = self.numpointsslider.value()
        func = self.funcedit.text()
        
        if self.debug:
            print(start, end, numpoints, func)


        xs = np.linspace(start, end, numpoints)

        self.syntaxerror = False


        def f(x):
            try:
                result = eval(func, {'__builtins__': None}, {"x": x, 'sin':np.sin, 'cos':np.cos, 'tan':np.tan, 'exp':np.exp})
                if str(result) == 'inf':
                    return 0
                return result
            except Exception as e:
                self.exception = e
                self.syntaxerror = True
                return 



        ys = [f(x) for x in xs]
        
        self.plotwidget.clear()
        if not self.syntaxerror:
            self.plotwidget.plot(xs, ys, pen={"color": "g","width": 3})
        elif self.debug:
            print(self.exception)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())