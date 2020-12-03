import sys
import threading

import numpy as np
import pandas as pd
import pkg_resources
from PyQt5 import QtWidgets, uic, QtCore
import pyqtgraph as pg
import click

from pythonlab.models.models import DiodeExperiment as DE

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self, debug=False):
        """Creates a UserInterface() instance, enables interactive functionality of ui."""

        super().__init__()
        self.debug = debug
        self.resource = None

        uic.loadUi(pkg_resources.resource_stream("pythonlab.views", "currentplotter.ui"), self)

        # Resources, following line takes long time, so some hard-coding:
        #self.resource_select.addItems(DE.get_resources(''))
        resources = ['ASRLCOM3::INSTR', 'ASRLCOM4::INSTR', 'ASRLCOM5::INSTR']
        self.resource_select.addItems(resources)

        # Identification
        self.identification_button.clicked.connect(self.get_identification)
        self.identification_line_edit.setReadOnly(True)

        # Used device
        self.identification_use_button.clicked.connect(self.set_device)
        self.selected_device_line_edit.setReadOnly(True)

        # Slider labels, there is no real clean way to do this:
        self.startslider.valueChanged.connect(lambda: self.start_value_label.setText(f"{self.startslider.value() / 100} V "))
        self.endslider.valueChanged.connect(lambda: self.end_value_label.setText(f"{self.endslider.value() / 100} V "))
        self.numpointsslider.valueChanged.connect(lambda: self.numpoints_value_label.setText(f"{self.numpointsslider.value()} "))

        # Prevents multiple measurements at the same time
        self.measuring = False
        self.measure_button.clicked.connect(self.plot_measurements)

        # Plot labels
        self.plotwidget.setLabel("left", "V out (V)")
        self.plotwidget.setLabel("bottom", "V in (V)")

        # Saving mechanism
        self.browsebutton.clicked.connect(self.file_select)
        self.savebutton.clicked.connect(self.save_data)


        # Threaded plotting
        self.xs, self.ys = [], []
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(lambda: self._plot(pen={"color": "g","width": 3}))
        self.plot_timer.start(100)
            
    def set_device(self):
        """Sets default resource (port), displays it"""
        self.resource = self.resource_select.currentText()
        self.selected_device_line_edit.setText(self.resource)

    def get_identification(self):
        """Gets the identification string of device, and displays it."""
        self.identification_line_edit.setText('')
        resource = self.resource_select.currentText()
        if self.debug:
            print(resource)

        # Unfortunately, this is very slow
        info = DE.get_info(resource)
        if self.debug:
            print(info)
            
        if info:
            self.identification_line_edit.setText(info)
        else:
            self.identification_line_edit.setText("Not Found!")

    def file_select(self):
        """Opens File Dialog box to select file. Displays path/to/file as well."""
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files(*.csv)")
        self.filename_line_edit.setText(self.filename)
        if self.debug:
            print(self.filename)
        
    def save_data(self):
        """Saves measured data to csv. If there is no data, no file is saved."""
        try:
            df = pd.DataFrame({"v_in": self.v_ins, "v_outs": self.v_outs})
        except AttributeError:
            return
        else:
            df.to_csv(self.filename, index=False)

    def plot_measurements(self):
        """Evokes pythonlab.models module to measure data over specified range, plots data was well. Has spam protection."""
        # The spam protection
        if not self.measuring:
            self.measuring = True
        else:
            return

        start = self.startslider.value() / 100
        end = self.endslider.value() / 100
        numpoints = self.numpointsslider.value()
        args = (start, end, numpoints)
        kwargs = {"pen": {"color": "g","width": 3}}

        self.xs, self.ys = [], []

        if self.debug:
            print(args)
        
        # Getting data, starting a thread
        self.xs = np.linspace(*args)
        self.get_data_thread = threading.Thread(target=self._get_data, args=args, kwargs={"port": self.resource})
        self.get_data_thread.start()

        # Function finished
        self.plot_timer.stop()
        self.measuring = False

    def _plot(self, **kwargs):
        print("_plot() activated!")
        self.plotwidget.clear()
        self.plotwidget.plot(self.xs[:len(self.ys)], self.ys, **kwargs)

    def _get_data(self, *args, **kwargs):
        """Adds new measured data to self.ys, in realtime."""
        for V_out in DE.get_voltages(*args, **kwargs):
            self.ys.append(V_out)
            print(f"New datapoint {V_out} added!")


# Click command        
@click.group()
def cli():
    pass


@cli.command()
def run():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface(debug=True)
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()

