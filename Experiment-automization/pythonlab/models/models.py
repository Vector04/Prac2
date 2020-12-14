"""Contains function evoked by pythonlab.views, computes results by evoking pythonlab.controllers."""

from pythonlab.controllers.arduino_device import ArduinoVISADevice
from pythonlab.controllers.prerecorded_device import PreRecordedDevice
import numpy as np
import time
import random
from uncertainties import ufloat, unumpy

# Note: The use of classes here is redundant in my opinion, as all the methods defined here need to function independently anyway. It is for this reason that all we only have classmethods here.


class DiodeExperiment:
    @classmethod
    def get_resources(cls, search):
        """Yields all the resources the ArduinoVISADevice() can find, filtered by the search query. Returns all the resources if search is None."""
        # Get resources
        resources = ArduinoVISADevice.get_resources()
        for resource in resources:
            if search in resource:
                # A generator symplifies the code in pythonlab.views
                yield resource

    @classmethod
    def get_info(cls, port):
        """Returns the device information of device on `port'."""
        # Exception handling if no connection can be made to the device.
        try:
            device = ArduinoVISADevice(port)
            return device.get_hardware_info()
        except:
            return

    @classmethod
    def get_current(cls, input_voltage, n, **kwargs):
        """Returns the measured current through the diode, with specified `input_voltage' applied. The current is measured `n' times."""
        device = ArduinoVISADevice(**kwargs)
        voltages = []
        for _ in range(n):
            # The pythonlab.controllers does all the real work here, really.
            device.set_output_voltage(voltage=input_voltage)
            voltages.append(device.measure_input_voltage(channel=2))

        device.set_output_voltage(voltage=0)
        v_mean = np.mean(voltages)

        # The std dev can be the std dev of all the measurements, or the
        # measurement resolution of the arduino. To play it save, we use the
        # largest, and apply the sqrt n rule
        v_std = max(np.std(voltages), 0.0033) / np.sqrt(n)

        # Current of diode = current of resistor = voltage / resistance.
        return v_mean / 220, v_std / 220

    @classmethod
    def get_voltages(cls, v_min, v_max, n, **kwargs):
        """Measures the voltage across the resistor when the input voltages is varied between `v_min' and `v_max', measurese at `n' different input voltages."""
        device = ArduinoVISADevice(**kwargs)
        for voltage in np.linspace(v_min, v_max, num=n):
            device.set_output_voltage(voltage=voltage)
            time.sleep(0.1)
            # Once again, a generator symplifies the code in pythonlab.views
            yield device.measure_input_voltage(channel=2)
        device.set_output_voltage(voltage=0)

# We need to implement a I,U plot,
# a P, U plot
# a Maximum point power tracking mechanism

Voltage_multiplier = 3
R_small = 4.7
value_to_voltage = 3.3 / 1023

class PVExperiment(DiodeExperiment): # Inheritance for get_info and get_resources methods
    @classmethod
    def get_volts_and_amps(self, v0_min, v0_max, n, port=None, dt=0.03, m=3):
        device = ArduinoVISADevice(port=port)
        for V_0 in np.linspace(v0_min, v0_max, n):
            device.set_output_voltage(channel=0, voltage=V_0)
            vs = []
            time.sleep(dt)
            for _ in range(m):
                v1 = device.measure_input_value(channel=1)  
                v2 = device.measure_input_value(channel=2)
                vs.append((v1, v2))
                time.sleep(dt / 3)
            # Data processing
            vs = np.array(vs) * value_to_voltage
            V_out = Voltage_multiplier * ufloat(np.mean(vs[:,0]), npstd(vs[:,0]))
            I_out = ufloat(np.mean(vs[:,1]), np.std(vs[:,1])) / R_small
            yield V_out, I_out
        device.set_output_voltage(channel=0, voltage=0)

    # A P, U plot can be created from a U,I plot, no need to reimplement the same thing.   

    @classmethod
    def get_volts_and_amps_fake(self, v0_min, v0_max, n, port=None, dt=0.03, m=3):
        device = PreRecordedDevice(port=port)
        for V_0 in np.linspace(v0_min, v0_max, n):
            device.set_output_voltage(0, V_0)
            vs = []
            time.sleep(dt)
            for _ in range(m):
                v1 = float(device.get_input_value(1))
                v2 = float(device.get_input_value(2))
                vs.append((v1, v2))
                time.sleep(dt / 3)
            # Data processing
            vs = np.array(vs) * value_to_voltage
            V_out = Voltage_multiplier * ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
            I_out = ufloat(np.mean(vs[:,1]), np.std(vs[:,1])) / R_small
            yield V_out, I_out
        device.set_output_voltage(0, 0)

# x = PVExperiment()
# for a in x.get_volts_and_amps_fake(0, 3.3, 10):
#     print(a)