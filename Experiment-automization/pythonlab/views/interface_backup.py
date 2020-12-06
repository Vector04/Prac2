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
        self.plot_timer.timeout.connect(
            lambda: self._plot(pen={"color": "g","width": 3}))
        self.plot_timer.start(100)
        # if event_flag = False ==> plotting is happening
        # if event_flag = True ==> device is free to use
        self.plot_event = threading.Event()
        self.plot_event.set()
        self.is_plotting = False

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
            if self.debug:
                print("Tried to save, but no data!")
            return
        else:
            try:
                df.to_csv(self.filename, index=False)
            except AttributeError:
                if self.debug:
                    print("No filename found, promting FileDialog!")
                if self.file_select():
                    self.save_data()
            else:
                if self.debug:
                    print("Save succesful!")

    def plot_measurements(self):
        """Evokes pythonlab.models module to measure data over specified range, plots data was well. Has spam protection."""
        print(f"plot_measurements() activated!")
        print(f"{self.plot_event.is_set() = }, {self.is_plotting = }")
        if not self.plot_event.is_set():
            print("aborting plot_measurements()")
            return
        self.plot_event.clear()
        self.is_plotting = True

        self.measure_button.setEnabled(False)
        self.plot_timer.start(100)

        start = self.startslider.value() / 100
        end = self.endslider.value() / 100
        numpoints = self.numpointsslider.value()
        args = (start, end, numpoints)

        self.xs, self.ys = [], []

        if self.debug:
            print(args)

        # Getting data, starting a thread
        self.xs = np.linspace(*args)
        self.get_data_thread = threading.Thread(
            target=self._get_data, args=args, kwargs={"port": self.resource})
        print("Thread Created!")
        self.get_data_thread.start()
        print("Thread Started!")

        # The following code needs to be exectud after the thread finishes.
        event_finished = self.plot_event.wait()
        print(f"{event_finished = }")
        # self.plot_timer.stop()
        self.measure_button.setEnabled(True)
        self.is_plotting = False

    def _plot(self, **kwargs):
        print("_plot activated!")
        self.plotwidget.clear()
        self.plotwidget.plot(self.xs[:len(self.ys)], self.ys, **kwargs)

    def _get_data(self, *args, **kwargs):
        """Adds new measured data to self.ys, in realtime."""
        for V_out in DE.get_voltages(*args, **kwargs):
            self.ys.append(V_out)
            if self.debug:
                print(f"New datapoint [{V_out}] added!")
        self.plot_event.set()


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
