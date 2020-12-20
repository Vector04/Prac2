"""Contains function evoked by pythonlab.views, computes results by evoking pythonlab.controllers."""

from pythonlab.controllers.arduino_device import ArduinoVISADevice
from pythonlab.controllers.prerecorded_device import PreRecordedDevice as FakeDevice
import numpy as np
import time
import random
from uncertainties import ufloat, unumpy

from matplotlib import pyplot as plt
fig, (ax1, ax2) = plt.subplots(ncols=2)
# Note: The use of classes here is redundant in my opinion, as all the methods defined here need to function independently anyway. It is for this reason that all we only have classmethods here.


class Experiment:
    """Base class for all other Experiment() classes. Contains the following classmethods:
        - `get_resources(cls, search)`: gets all available resources. 
        - `get_info(cls, port)`: gets device identification string. 
    """
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
            if port == 'Pre-recorded':
                x = PreRecordedDevice()
                return x.get_identification()
            return


class DiodeExperiment(Experiment):
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

# PVExperiment parameters
Voltage_multiplier = 3
R_small = 4.7
value_to_voltage = 3.3 / 1023

# Make sure fake an real devices behave the same way:

class PreRecordedDevice(FakeDevice):
    def set_output_voltage(self, channel=0, voltage=0):
        """Set the voltage for a DAC output channel.

        This differs from :meth:`set_output_value` in that this method sets the
        voltage, not a raw DAC value.

        Args:
            channel (int): The output channel. Channel numbering starts at 0.
            value (float): The DAC voltage (range 0 - 3.3 V).

        Returns:
            The devices' response. Typically the device echoes back the value.
        """
        return super().set_output_voltage(channel, voltage)

    def measure_input_value(self, channel=0):
        """Get the value measured on an ADC input channel.

        Args:
            channel (int): The input channel. Channel numbering starts at 0.

        Returns:
            The integer value measured for the channel (range 0 - 1023),
            where 0 is the device's GND and 1023 is the device's operating
            voltage (3.3 V).
        """
        return super().get_input_value(channel)


class PVExperiment(Experiment): 
    """Controls the Photo-Voltaic cell experiment. Has the following methods:
        - `get_volts_and_amps`: yiels the voltages and currents over a range of different input voltages.
        - `get_power`: returns the power outputted by the PV Device.
        - `max_power`: finds the optimal input voltage to maximise power output of PV Device.
    """
    def __init__(self, port, **kwargs):
        """Creates a new PVExperiment() Instance. 
        Arguments: 
         - `port`: The port from which the visa device can be accessed. 
                   Can also be equal to 'Pre-recorded' to use the prerecorded device.
        Returns:
          - A new PVExperiment() instance. 
        """ 
        if port == 'Pre-recorded':
            self.device = PreRecordedDevice()
            self.device.set_output_voltage(channel=0, voltage=1.6)
        else:
            self.device = ArduinoVISADevice(port=port)

    def get_volts_and_amps(self, v0_min, v0_max, n, dt=0.03, m=4, **kwargs):
        """Gets ouput voltage and current of PV device over a range of input voltages.
        Arguments:
         - `V0_min`: start of voltage-vary range.
         - `V0_max`: end of voltage-vary range.
         - `n`: amount of different voltages in voltage-vary range.
         - `dt=0.03`: time wait between different measurements
         - `m=4`: amount of times to repeat each hmeasurement.
        Yields:
         - (V_out, I_out): a tupe of ufloat() objects. The output voltage and current.
        """
        for V_0 in np.linspace(v0_min, v0_max, n):
            self.device.set_output_voltage(channel=0, voltage=V_0)
            vs = []
            time.sleep(dt)
            for _ in range(m):
                v1 = float(self.device.measure_input_value(channel=1))
                v2 = float(self.device.measure_input_value(channel=2))
                vs.append((v1, v2))
                time.sleep(dt / 3)
            # Data processing
            vs = np.array(vs) * value_to_voltage
            V_out =  ufloat(np.mean(vs[:,0]), np.std(vs[:,0])) * Voltage_multiplier
            I_out = ufloat(np.mean(vs[:,1]), np.std(vs[:,1])) / R_small
            yield V_out, I_out
        self.device.set_output_voltage(channel=0, voltage=0)

    def get_power(self, V_in=None, m=4, dt=0, return_more=False):
        """Gets the outgoing power of the PV Device.
        Arguments:
         - `V_in`=None: The ingoing Voltage. Can be left to None if one wishes to just measure the power.
         - `m=4': The amount of times to repeat the voltage and current measurements.
         - `dt=0`: The amount of time to wait in between each measurment.
         - `return_more=False`: If true, returns the voltage and current instead of the power.
        Returns:
         - If return_more = False: A ufloat() object, the power output of the PV Device.
         - If return_more = True: A tuple of ufloat() objects, the voltage and current of The PV Device.
        """
        vs = []
        if V_in is not None:
            self.device.set_output_voltage(channel=0, voltage=V_in)
        for _ in range(m):
            v1 = float(self.device.measure_input_value(channel=1))
            v2 = float(self.device.measure_input_value(channel=2))
            vs.append((v1, v2))
            time.sleep(dt)
        vs = np.array(vs) * value_to_voltage
        V1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
        V2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1])) 
        if return_more:
            return V1 * Voltage_multiplier, V2 / R_small 
        return V1 * V2 * Voltage_multiplier / R_small

    def max_power(self, a=1.6, b=1.9, optimized_threshold=0.05, m=4, dt=0):
        """Sets the optimal V_in for maximum power output.
        Arguments:
         - `a`: The lowerbound of the initial V_in checking range.
         - `b`: The upperbound of the initial V_in checking range.
         - `optimzed_threshold`: How close a and b need to be before the we conclude V_optimum has converged. 
                                 Needs to be greater than 0.
         - `m=4`: Amount of times to repeat each measurment when calculating the power.
         - `dt=0`: Waiting time between each measurment.
        Returns:
           None. Just sets the optimum V_in.
        """
        while b - a > optimized_threshold:
            P_a = self.get_power(V_in=a, m=m, dt=dt).n
            P_b = self.get_power(V_in=b, m=m, dt=dt).n
            if P_b > P_a: 
                a = (a + b) / 2
            else:
                b = (a + b) / 2
        print(f"New V_0 = {(a + b) / 2}")
        self.device.set_output_voltage(0, (a + b) / 2)