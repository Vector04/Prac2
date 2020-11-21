"""Contains function evoked by pythonlab.views, computes results by evoking pythonlab.controllers."""

from pythonlab.controllers.arduino_device import ArduinoVISADevice
import numpy as np 

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
        except Exception as e:
            return  
        return device.get_hardware_info()

    @classmethod
    def get_current(cls, input_voltage, n):
        """Returns the measured current through the diode, with specified `input_voltage' applied. The current is measured `n' times."""
        device = ArduinoVISADevice()
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
    def get_voltages(cls, v_min, v_max, n):
        """Measures the voltage across the resistor when the input voltages is varied between `v_min' and `v_max', measurese at `n' different input voltages."""
        device = ArduinoVISADevice()
        voltages = []
        for voltage in np.linspace(v_min, v_max, num=n):
            device.set_output_voltage(voltage=voltage)
            # Once again, a generator symplifies the code in pythonlab.views
            yield device.measure_input_voltage(channel=2)
        device.set_output_voltage(voltage=0)