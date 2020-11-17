from pythonlab.controllers.arduino_device import ArduinoVISADevice
import numpy as np 

class DiodeExperiment:
    @classmethod
    def get_resources(cls, search):
        resources = ArduinoVISADevice.get_resources()
        for resource in resources:
            if search in resource:
                yield resource

    @classmethod
    def get_info(cls, port):
        try:
            device = ArduinoVISADevice(port)
        except Exception as e:
            return 
        return device.get_hardware_info()

    @classmethod
    def get_current(cls, input_voltage, n):
        device = ArduinoVISADevice()
        voltages = []
        for _ in range(n):
            device.set_output_voltage(voltage=input_voltage)
            voltages.append(device.measure_input_voltage(channel=2))
        device.set_output_voltage(voltage=0)
        v_mean = np.mean(voltages) 
        v_std = max(np.std(voltages), 0.0033) / np.sqrt(n)

        return v_mean / 220, v_std / 220

    @classmethod
    def get_voltages(cls, v_min, v_max):
        device = ArduinoVISADevice()
        voltages = []
        for voltage in np.linspace(v_min, v_max, 15):
            device.set_output_voltage(voltage=voltage)
            yield device.measure_input_voltage(channel=2)  
        device.set_output_voltage(0)
