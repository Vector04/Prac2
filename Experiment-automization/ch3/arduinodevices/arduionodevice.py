import numpy as np
import pyvisa
import time
from matplotlib import pyplot as plt
import pandas as pd
from pythonlab.controllers import ArduinoVISADevice


class ArduinoVISADevice:
    """A wrapper class to give commands to an Arduino using the VISA interface. Uses pyvisa.
        Usage: 
            devicedevice = ArduinoVISADevice(port=None)
            device.set_output_value(channel=0, value=512)
            volt_ch0 = device.get_output_voltage(channel=0)
    """

    def __init__(self, port=None):
        """Instantiates a connection between the instance and the arduino."""
        self.rm = pyvisa.ResourceManager("@py")
        if not port:
            port = self.rm.list_resources()[-1]
        self.device = self.rm.open_resource(
            port, read_termination="\r\n", write_termination="\n")

    def set_output_value(self, channel=0, value=600):
        """Sets the output voltage of channel to value."""
        return self.device.query(f"OUT:CH{channel} {value}")

    def get_output_voltage(self, channel=1):
        """Returns the voltage of the channel specified."""
        return float(self.device.query(f"MEAS:CH{channel}:VOLT?"))

    def get_input_voltage(self, channel=0):
        """Returns the voltage of the channel specified."""
        return float(self.device.query(f"MEAS:CH{channel}:VOLT?"))


device = ArduinoVISADevice()
device.set_output_value(channel=0, value=512)
volt_ch0 = device.get_output_voltage(channel=0)
volt_ch2 = device.get_output_voltage(channel=2)
print(volt_ch0, volt_ch2)
help(ArduinoVISADevice)
