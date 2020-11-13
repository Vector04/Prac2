"""
Contains the ArduinoVISADevice class.
Usage:
    devicedevice = ArduinoVISADevice(port=None)
    device.set_output_value(channel=0, value=512)
    volt_ch0 = device.get_output_voltage(channel=0)
"""

import pyvisa


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
            # print(self.rm.list_resources())
        self.device = self.rm.open_resource(
            port, read_termination="\r\n", write_termination="\n")

    def query(self, query):
        """Can directly any command, should this be neccesary."""
        return self.device.query(query)

    def get_hardware_info(self):
        """Returns the hardware info of the device."""
        return self.device.query("*IDN?")

    def set_output_value(self, channel=0, value=600):
        """Sets the output value (Between 0 and 1023) of channel to value."""
        return self.device.query(f"OUT:CH{channel} {value}")

    def set_output_voltage(self, channel=0, voltage=2.0):
        """Sets the output voltage (Between 0 and 3.3V) of channel to value."""
        return self.device.query(f"OUT:CH{channel}:VOLT {voltage}")

    def get_output_value(self, channel=0):
        """Returns the ouput value (Between 0 and 1023) of the channel specified."""
        return int(self.device.query(f"OUT:CH{channel}?"))

    def get_output_voltage(self, channel=0):
        """Returns the output voltage (Between 0 and 3.3 V) of the channel specified."""
        return float(self.device.query(f"OUT:CH{channel}:VOLT?"))

    def measure_input_value(self, channel=0):
        """Returns the measured value (Between 0 and 1023) of the channel specified."""
        return int(self.device.query(f"MEAS:CH{channel}?"))

    def measure_input_voltage(self, channel=1):
        """Returns the measured voltage (Between 0 and 3.3 V) of the channel specified."""
        return float(self.device.query(f"MEAS:CH{channel}:VOLT?"))
