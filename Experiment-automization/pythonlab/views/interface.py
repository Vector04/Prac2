import sys
import logging
import time

import numpy as np
import pandas as pd
import pkg_resources
from PyQt5 import QtWidgets, uic, QtCore
import pyqtgraph as pg
import click
import serial
from uncertainties import ufloat, unumpy

from pythonlab.models.models import DiodeExperiment as PE
from pythonlab.models.models import PVExperiment as PE
from pythonlab.views.helpers import *

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

# Logging, only by the root.
for logger in logging.Logger.manager.loggerDict:
    logging.getLogger(logger).disabled = True


class UserInterface(QtWidgets.QMainWindow):
    """Controls functionality of our QApplication. implements logic that enables the features of the user interface.
        Features are:
            - Port scanning and selection
            - Port verification
            - Scanning voltage range adjustment
            - Live result display with errorbars
            - Data export capabilities.
    """

    def __init__(self):
        """Creates a UserInterface() instance, enables interactive functionality of ui."""

        super().__init__()
        self.resource = None

        uic.loadUi(pkg_resources.resource_stream(
            "pythonlab.views", "currentplotter.ui"), self)

        # Resources, following line takes long time:
        # self.resource_select.addItems(PE.get_resources('') + ['Pre-recorded'])
        # Some alternative hardcoding for testing purposes may be desirable:
        resources = ['ASRLCOM3::INSTR', 'ASRLCOM4::INSTR', 'ASRLCOM5::INSTR', 'Pre-recorded']
        self.resource_select.addItems(resources)

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
        self.plotting_options1 = {"pen": {"color": "g", "width": 3}}
        self.plotting_options11 = {"pen": {"color": "g", "width": 2}}
        self.plotting_options2 = {"pen": {"color": "r", "width": 3}}
        self.plotting_options21 = {"pen": {"color": "r", "width": 2}}
        self.plotting_options3 = {"pen": {"color": "#2a78f5", "width": 2}}

        # Plot labels
        self.plotwidget.setLabel("left", "V out (V), I out (A)")
        self.plotwidget.setLabel("bottom", "V in (V)")
        self.plotwidget2.setLabel("left", "I out (A)")
        self.plotwidget2.setLabel("bottom", "V out (V)")
        self.plotwidget3.setLabel("left", "P out (W)")
        self.plotwidget3.setLabel("bottom", "V out (V)")
        self.plotwidget4.setLabel("left", "P out (W)")
        self.plotwidget4.setLabel("bottom", "R out (Ω)")
        self.plotwidget.addLegend()

        # Saving mechanism
        self.browsebutton.clicked.connect(self.file_select)
        self.savebutton.clicked.connect(self.save_data)

        # Fit phase diagram
        self.startfit_button.clicked.connect(self.add_fit)
        self.fitresults_linedit.setReadOnly(True)

    def set_device(self):
        """Sets default resource (port), displays it"""
        self.resource = self.resource_select.currentText()
        self.selected_device_line_edit.setText(self.resource)
        logging.info(f"Device {self.resource} set.")

    def get_identification(self):
        """Gets the identification string of device, and displays it."""
        self.identification_line_edit.setText('')
        resource = self.resource_select.currentText()
        logging.debug(f"Getting Identification for {resource}.")

        # Unfortunately, this is very slow
        info = PE.get_info(resource)

        if info:
            self.identification_line_edit.setText(info)
            logging.info(f"Identification for {resource} is {info}.")
        else:
            self.identification_line_edit.setText("Not Found!")
            logging.warning(f"No Identification found for {resource}.")

    def file_select(self):
        """Opens File Dialog box to select file. Displays path/to/file as well."""
        logging.debug(f"Propting to get filename.")
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            filter="CSV files(*.csv)")
        self.filename_line_edit.setText(self.filename)
        logging.debug(f"Filename is {self.filename}.")

        # Useful, see the save_data method
        return self.filename

    def save_data(self):
        """Saves measured data to csv. If there is no data, no file is saved."""
        try:
            df = pd.DataFrame({"v_in": self.xs, "V_out": self.Vs, 
                            "dV_out": self.dVs, "I_out": self.Is, "dI_out": self.dIs})
        except AttributeError:
            # There is no data to be saved
            logging.debug("There is no data to be saved.")
            return
        else:
            try:
                df.to_csv(self.filename, index=False)
            except AttributeError:
                # self.filename is not defined, ask again
                logging.debug("No filename found, promting a FileDialog.")
                if self.file_select():
                    self.save_data()
            else:
                # Give user feedback that data was saved succesfully
                self.savebutton.setStyleSheet("background-color: #76fa34")
                logging.info("Data saved succesfully!")

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
        # Simplifies saving function
        self.xs = np.linspace(*args)

        self.measure_button.setEnabled(False)
        self.plotwidget.clear()
        # reset save button color if there was a succesful save previously
        self.savebutton.setStyleSheet("")
        self.plot_timer.start(100)

        logging.debug(f"Scan parameters: {args}.")

        # Note: This was where I had trouble with threading, I implemented a better and more elegant solution.
        # Instantiating data collection thread
        self.data_thread = DataCollectionThread(*args, port=self.resource)

        # Connecting signals, now the _plot() function only activates if there is new data
        self.data_thread.ys_signal.connect(self._plot)
        self.data_thread.ys_signal.connect(self.copy_ys)
        self.data_thread.finished.connect(self.end_measurement)

        self.data_thread.start()
        logging.info(f"Starting data Scan.")

    def end_measurement(self):
        """Activates miscellaneous functions to properly finish the measurement."""
        self.measure_button.setEnabled(True)
        self.plot_timer.stop()
        self.is_plotting = False
        logging.info(f"Finished data scan.")

    @staticmethod
    def _make_errorbaritem(xs, ys, **kwargs):
        """Returns and Pg.Errorbaritem, made from xs(uarray) and ys (uarray). Can also pass in plotting options."""
        return pg.ErrorBarItem(x=unumpy.nominal_values(xs), y=unumpy.nominal_values(ys),
            width=unumpy.std_devs(xs) * 2, height=unumpy.std_devs(ys) * 2, **kwargs)

    def _plot(self, Vs, dVs, Is, dIs):
        """Plots the given data on plotwidget instance.
        Arguments:
            `Vs': list, Voltage.
            `dVs': list, uncertainty of voltage.
            `Is': list, current.
            `dIs': list, uncertainty of current.
        """
        logging.debug("_plot() activated.")
        self.plotwidget.clear()
        self.plotwidget2.clear()
        self.plotwidget3.clear()
        self.plotwidget4.clear()
        
        self.plotwidget.plot(self.xs[:len(Vs)], Vs, **self.plotting_options1, name="V out (V)")
        self.plotwidget.plot(self.xs[:len(Is)], Is, **self.plotting_options2, name="I out (A)")

        Vs = unumpy.uarray(Vs, dVs)
        Is = unumpy.uarray(Is, dIs)
        Ps = Vs * Is
        Rs = Vs / Is

        self.plotwidget.addItem(self._make_errorbaritem(self.xs[:len(Vs)], Vs, **self.plotting_options11))
        self.plotwidget.addItem(self._make_errorbaritem(self.xs[:len(Vs)], Is, **self.plotting_options21))
        self.plotwidget2.addItem(self._make_errorbaritem(Vs, Is, **self.plotting_options3))
        self.plotwidget3.addItem(self._make_errorbaritem(Vs, Ps, **self.plotting_options3))
        self.plotwidget4.addItem(self._make_errorbaritem(Rs, Ps, **self.plotting_options3))

    def copy_ys(self, Vs, dVs, Is, dIs):
        """Copies data from DataCollectionThread to self.ys attribute.
        Arguments:
            `Vs': list, Voltage.
            `dVs': list, uncertainty of voltage.
            `Is': list, current.
            `dIs': list, uncertainty of current.
        """
        self.Vs = Vs
        self.dVs = dVs
        self.Is = Is
        self.dIs = dIs

    def add_fit(self):
        """Adds fit for U-I plot. Evokes helpers.fit_phase_diagram()."""
        try:
            self.Vs
        except AttributeError:
            return
        fit_report, (fit_Vs, fit_Is) = fit_phase_diagram(self.Vs, self.dVs, self.Is, self.dIs)
        self.fitresults_linedit.setText(fit_report)
        self.plotwidget2.plot(fit_Vs, fit_Is, **self.plotting_options1)


class DataCollectionThread(QtCore.QThread):
    """QThread subclass to collect data asynchonously"""
    ys_signal = QtCore.pyqtSignal(list, list, list, list)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.Vs, self.dVs = [], []
        self.Is, self.dIs = [], []
        self.PE = PE(**self.kwargs)
        

    def __del__(self):
        self.wait()

    def run(self):
        """Collects Data."""
        try:
            for V_out, I_out in self.PE.get_volts_and_amps(*self.args, **self.kwargs):
                self.Vs.append(V_out.n)
                self.dVs.append(V_out.s)
                self.Is.append(I_out.n)
                self.dIs.append(I_out.s)
                self.ys_signal.emit(self.Vs, self.dVs, self.Is, self.dIs)
                logging.debug(f"New datapoint [{V_out}] added.")
        except serial.serialutil.SerialException:
            logging.error(f"Cannot measure any data on port {self.kwargs['port']}.")

@click.group()
def cli():
    pass


@cli.command()
@click.option("--log", default='warning', type=str, help="The logging level.")
def run(log='debug'):
    """Runs the application. 
    Option `log' represents the logging level. It can be left blank, or set to one of the following:
    debug, info, warning, error, critical.
     """
    logging.basicConfig(level=getattr(logging, log.upper()))
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
