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

        uic.loadUi(pkg_resources.resource_stream(
            "pythonlab.views", "currentplotter.ui"), self)

        # Resources, following line takes long time:
        self.resource_select.addItems(DE.get_resources(''))
        # Some alternative hardcoding for testing purposes may be desirable:
        # resources = ['ASRLCOM3::INSTR', 'ASRLCOM4::INSTR', 'ASRLCOM5::INSTR']
        # self.resource_select.addItems(resources)

        # Identification
        self.identification_button.clicked.connect(self.get_identification)
        self.identification_line_edit.setReadOnly(True)

        # Used device
        self.identification_use_button.clicked.connect(self.set_device)
        self.selected_device_line_edit.setReadOnly(True)

        # Slider labels, there is no real clean way to do this:
        self.startslider.valueChanged.connect(
            lambda: self.start_value_label.setText(
                f"{self.startslider.value() / 100} V "))
        self.endslider.valueChanged.connect(
            lambda: self.end_value_label.setText(
                f"{self.endslider.value() / 100} V "))
        self.numpointsslider.valueChanged.connect(
            lambda: self.numpoints_value_label.setText(
                f"{self.numpointsslider.value()} "))

        # Main plotting function
        self.measure_button.clicked.connect(self.start_measurement)
        self.plot_timer = QtCore.QTimer()
        self.is_plotting = False
        self.plotting_options = {"pen": {"color": "g","width": 3}}

        # Plot labels
        self.plotwidget.setLabel("left", "V out (V)")
        self.plotwidget.setLabel("bottom", "V in (V)")

        # Saving mechanism
        self.browsebutton.clicked.connect(self.file_select)
        self.savebutton.clicked.connect(self.save_data)

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
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            filter="CSV files(*.csv)")
        self.filename_line_edit.setText(self.filename)
        # Useful, see the save_data method
        return self.filename
        if self.debug:
            print(self.filename)

    def save_data(self):
        """Saves measured data to csv. If there is no data, no file is saved."""
        try:
            df = pd.DataFrame({"v_in": self.xs, "v_out": self.ys})
        except AttributeError:
            # There is no data to be saved
            if self.debug:
                print("Tried to save, but no data!")
            return
        else:
            try:
                df.to_csv(self.filename, index=False)
            except AttributeError:
                # self.filename is not defined, ask again
                if self.debug:
                    print("No filename found, promting FileDialog!")
                if self.file_select():
                    self.save_data()
            else:
                # Give user feedback that data was saved succesfully
                self.savebutton.setStyleSheet("background-color: #76fa34")
                if self.debug:
                    print("Save succesful!")

    def start_measurement(self):
        """Evokes pythonlab.models module to measure data over specified range, plots data was well. Has spam protection."""

        # Simple spam protection
        if self.is_plotting:
            return
        self.is_plotting = True

        # Getting plot parameters from sliders
        start = self.startslider.value() / 100
        end = self.endslider.value() / 100
        numpoints = self.numpointsslider.value()
        args = (start, end, numpoints)
        # Simplifies plotting function
        self.xs = np.linspace(*args)
        # Copy of data, useful when saving data
        self.ys = []

        self.measure_button.setEnabled(False)
        # reset save button color if there was a succesful save previously
        self.savebutton.setStyleSheet("")
        self.plot_timer.start(100)

        if self.debug:
            print(args)

        # Note: This was where I had trouble with threading, I implementen a better and more elegant solution.
        # Instantiating data collection thread
        self.data_thread = DataCollectionThread(*args, port=self.resource)

        # Connecting signals, now the _plot() function only activates if there is new data
        self.data_thread.ys_signal.connect(self._plot)
        self.data_thread.ys_signal.connect(self.copy_ys)
        self.data_thread.finished.connect(self.end_measurement)

        self.data_thread.start()

    def end_measurement(self):
        """Activates miscellaneous functions to properly finish the measurement."""
        self.measure_button.setEnabled(True)
        self.plot_timer.stop()
        self.is_plotting = False

    def _plot(self, ys):
        """Plots the given data on plotwidget instance.
        Arguments:
            `ys': list, the data to plot. 
        """
        self.plotwidget.clear()
        self.plotwidget.plot(self.xs[:len(ys)], ys, **self.plotting_options)

    def copy_ys(self, ys):
        """Copies data from DatacollectionThread to Userinterface.ys attribute.
        Arguments:
            `ys': list, the data to be copied. 
        """
        self.ys = ys


class DataCollectionThread(QtCore.QThread):
    ys_signal = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.ys = []

    def __del__(self):
        self.wait()

    def run(self):
        for V_out in DE.get_voltages(*self.args, **self.kwargs):
            self.ys.append(V_out)
            self.ys_signal.emit(self.ys)

# Click command


@ click.group()
def cli():
    pass


@ cli.command()
def run():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface(debug=True)
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
