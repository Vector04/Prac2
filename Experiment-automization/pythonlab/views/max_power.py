import sys
import logging
import time
import random

import numpy as np
import pandas as pd
import pkg_resources
from PyQt5 import QtWidgets, uic, QtCore
import pyqtgraph as pg
import click


from pythonlab.models.models import PVExperiment as PE
from pythonlab.views.helpers import *



for logger in logging.Logger.manager.loggerDict:
    logging.getLogger(logger).disabled = True


pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class UserInterface(QtWidgets.QMainWindow):
    """Controls functionality of our QApplication. implements logic that enables the features of the user interface.
        Features are:
            - Port scanning and selection
            - Port verification
            - Power display and tracking
            - Resistance display and tracking
    """

    def __init__(self):
        """Creates a UserInterface() instance, enables interactive functionality of ui."""

        super().__init__()
        self.resource = None

        uic.loadUi(pkg_resources.resource_stream(
            "pythonlab.views", "powertracker.ui"), self)

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

        # Plot labels
        self.plotwidget.setLabel("left", "Power (W)")
        self.plotwidget.setLabel("bottom", "time (s)")
        self.plotwidget.setYRange(min=0, max=0.2)

        self.plotwidget2.setLabel("left", "Resistance (Ω)")
        self.plotwidget2.setLabel("bottom", "time (s)")
        self.plotwidget2.setYRange(min=0, max=2e3)

        # Start power tracking
        self.measure_button.clicked.connect(self.start_measurement)

        self.queue_P = Queue(20)
        self.queue_R = Queue(20)
        self.power_timer = QtCore.QTimer()
        self.power_timer.timeout.connect(self.collect_measurements)
        self.power_freq = 500

        self.power_max_timer = QtCore.QTimer()
        self.power_max_freq = 5000

        self.plotting_options = {"pen": {"color": "r", "width": 3}}
        self.plotting_options2 = {"pen": {"color": "r", "width": 2}}

        self.measuring = False


    def set_device(self):
        """Sets default resource (port), displays it"""
        if not self.measuring:
            self.resource = self.resource_select.currentText()
            self.selected_device_line_edit.setText(self.resource)
            logging.info(f"Device {self.resource} set.")
            self.queue_P = Queue(20)
            self.queue_R = Queue(20)

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


    def collect_measurements(self):
        """Calls the PE.get_power function to track the power output. Saves data to self.queue_P and slef.queue_R. """
        V, I  = self.PE.get_power(return_more=True)
        # In case I = 0
        try:
            power, resistance = V * I, V / I
        except ZeroDivisionError:
            power, resistance = ufloat(0, 0), ufloat(0,0)

        # Save and display data
        self.queue_P.add(power)
        self.queue_R.add(resistance)
        self.powerdisplay.setText(f"{power.n:.4f} \u00B1 {power.s:.4f} W")
        self.resistancedisplay.setText(f"{str(int(resistance.n)).rjust(4)} \u00B1 {str(int(resistance.s)).rjust(4)} Ω")
        self.plot()

    def plot(self):
        """Plots the power output and resistance of PV Device."""
        # Power
        xs = (np.arange(0, len(self.queue_P), 1) - len(self.queue_R)) * (self.power_freq / 1000) 
        self.plotwidget.clear()
        self.plotwidget.plot(xs, [x.n for x in self.queue_P.to_array()], **self.plotting_options)
        errorbars = pg.ErrorBarItem(
            x=xs, y=np.array([x.n for x in self.queue_P.to_array()]),
            height=np.array([x.s for x in self.queue_P.to_array()]) * 2, **self.plotting_options2)
        self.plotwidget.addItem(errorbars)
        self.plotwidget.setYRange(min=0, max=max(0.2, max([x.n for x in self.queue_P.to_array()])))
        
        # Resistance
        self.plotwidget2.clear()
        self.plotwidget2.plot(xs, [x.n for x in self.queue_R.to_array()], **self.plotting_options)
        errorbars = pg.ErrorBarItem(
            x=xs, y=np.array([x.n for x in self.queue_R.to_array()]),
            height=np.array([x.s for x in self.queue_R.to_array()]) * 2, **self.plotting_options2)
        self.plotwidget2.addItem(errorbars)
        self.plotwidget2.setYRange(min=0, max=max(2e3, 1.1*max([x.n + x.s for x in self.queue_R.to_array()])))


    def start_measurement(self):
        """Starts the live measurments. Can be evoked a 2nd time to stop the live measurement."""
        if not self.measuring:
            self.PE = PE(port=self.resource)
            self.power_timer.start(self.power_freq)
            self.power_max_timer.timeout.connect(self.PE.max_power)
            self.power_max_timer.start(self.power_max_freq)
            self.measure_button.setText("Stop")
            self.measure_label.setText("Stop power tracking")
            self.measuring = True
        else:
            self.power_timer.stop()
            self.power_max_timer.stop()
            self.measure_button.setText("Start")
            self.measure_label.setText("Start power tracking")
            self.measuring = False


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
