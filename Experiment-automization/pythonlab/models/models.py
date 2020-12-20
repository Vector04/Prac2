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

# We need to implement a I,U plot,
# a P, U plot
# a Maximum point power tracking mechanism

Voltage_multiplier = 3
R_small = 4.7
value_to_voltage = 3.3 / 1023

# Make sure fake an real devices behave the same way:

class PreRecordedDevice(FakeDevice):
    def set_output_voltage(self, channel=0, voltage=0):
        return super().set_output_voltage(channel, voltage)

    def measure_input_value(self, channel=0):
        return super().get_input_value(channel)


class PVExperiment(Experiment): 
    def __init__(self, port, **kwargs):
        if port == 'Pre-recorded':
            self.device = PreRecordedDevice()
            self.device.set_output_voltage(channel=0, voltage=1.6)
        else:
            self.device = ArduinoVISADevice(port=port)

    def get_volts_and_amps(self, v0_min, v0_max, n, dt=0.03, m=3, **kwargs):
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

    def get_power(self, V_in=None, m=4, dt=0):
        vs = []
        if V_in is not None:
            self.device.set_output_voltage(channel=0, voltage=V_in)
        for _ in range(m):
            v1 = float(self.device.measure_input_value(channel=1))
            v2 = float(self.device.measure_input_value(channel=2))
            vs.append((v1, v2))
            time.sleep(dt / 3)
        vs = np.array(vs) * value_to_voltage
        V1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
        V2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1]))
        P =  V1 * V2 * Voltage_multiplier / R_small
        return P

    def max_power(self, a=1.6, b=1.9, optimized_threshold=0.05, m=4, dt=0):
        while b - a > optimized_threshold:
            P_a = self.get_power(V_in=a, m=m, dt=dt).n
            P_b = self.get_power(V_in=b, m=m, dt=dt).n
            if P_b > P_a: 
                a = (a + b) / 2
            else:
                b = (a + b) / 2

        self.device.set_output_voltage(0, (a + b) / 2)

#     # A P, U plot can be created from a U,I plot, no need to reimplement the same thing.   

# # x = PVExperiment()
# # for a in x.get_volts_and_amps_fake(0, 3.3, 10):
# #     print(a)
#     @classmethod
#     def max_power_fake(self, port=None):
#         device = PreRecordedDevice(port=port)
#         dt = 0.03
#         m = 10
#         optimized_threshold = 0.0
#         max_tries = 10
#         V_0 = 5 / 3

#         current_P, current_V, new_V = None, None, V_0 
#         Vs_track = [V_0]
#         Ps_track = []

#         def power(vs):
#             vs = np.array(vs)
#             v1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
#             v2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1]))
#             return  v1 * v2 * Voltage_multiplier / R_small * value_to_voltage


        
#         for z in range(max_tries):
           
#             # Measure power
#             device.set_output_voltage(0, new_V)
#             vs = []
#             for _ in range(m):
#                 v1 = float(device.get_input_value(1))
#                 v2 = float(device.get_input_value(2))
#                 vs.append((v1, v2))
#                 time.sleep(dt / 3)
           
#             new_P = power(vs)
#             Ps_track.append(new_P.n)
#             print(f"V_in: {new_V} V. New Power: {new_P}")
#             ax2.errorbar(new_V, new_P.n, yerr=new_P.s, fmt='o')
            
#             if current_P is None:
#                 current_P = new_P
#                 current_V = new_V
#                 new_V += 0.05

#                 continue

#             # check how mush the power output has changed:
#             if abs((new_P - current_P).n) < optimized_threshold:
#                 break
#                 print(f"Converged!")

#             # otherwise, keep going.
#             print(f"Updating V_in")

#             def get_new_V(current_V, new_V, current_P, new_P):
#                 print(f"Delta V = {new_V - current_V}, delta P = {new_P - current_P}")

#                 dPdV = (new_P - current_P) / (new_V- current_V)
#                 # Assert that P has chaned significantly




#             get_new_V(current_V, new_V, current_P, new_P)

#             snr = 2 * abs(new_P.n - current_P.n) / (new_P.s + current_P.s)
#             print(f"snr: {snr}")
#             if snr < 0.5:
#                 print(f"converged-ish, P = {new_P}")
#                 break

#             new_V, current_V = (new_V + (1e-6*(new_P - current_P) / (new_V- current_V)).n, new_V)
#             current_P = new_P
#             Vs_track.append(new_V)

#         # ax1.plot(np.arange(0, max_tries, 1), Ps_track)

#     @classmethod
#     def max_power_fake2(self, port=None):
#         device = PreRecordedDevice(port=port)
#         dt = 0.0
#         m = 2
#         optimized_threshold = 0.0
#         max_tries = 10
#         V_0 = 5 / 3

#         current_I, current_U = None, None
#         Is_track = []
#         Us_track = []

#         def IU(vs):
#             vs = np.array(vs)
#             v1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0])) * value_to_voltage
#             v2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1])) * value_to_voltage
#             return v2 / R_small, v1 * Voltage_multiplier


        
#         for new_V in np.linspace(1.6, 1.9, 20):
           
#             # Measure power
#             device.set_output_voltage(0, new_V)
#             vs = []
#             for _ in range(m):
#                 v1 = float(device.get_input_value(1))
#                 v2 = float(device.get_input_value(2))
#                 vs.append((v1, v2))
#                 time.sleep(dt / 3)
           
#             new_I, new_U = IU(vs)

#             if current_I is not None:
                
#                 rel_I = (new_I - current_I) / new_I
#                 rel_U = (current_U - new_U) / new_U
#                 # print(f"dI/I: {rel_I}  dU/U: {rel_U}")
#                 print(rel_U.n)
#                 Is_track.append(rel_I)
#                 Us_track.append(rel_U)
#             current_I, current_U = new_I, new_U

#         Is_track = np.array(Is_track)
#         Us_track = np.array(Us_track)
#         ax1.errorbar(np.linspace(1.6, 1.9, 19), unumpy.nominal_values(Is_track), yerr=unumpy.std_devs(Is_track))
#         ax1.errorbar(np.linspace(1.6, 1.9, 19), unumpy.nominal_values(Us_track), yerr=unumpy.std_devs(Us_track))
#         ax2.errorbar(np.linspace(1.6, 1.9, 19), unumpy.nominal_values(Is_track - Us_track), yerr=unumpy.std_devs(Is_track - Us_track))

#     def max_power_fake3(self, port=None):
#         device = PreRecordedDevice(port=port)
#         dt = 0.0
#         m = 10
#         optimized_threshold = 0.005
#         max_tries = 10
#         V_0 = 5 / 3

#         a, b = 1.6, 1.9
#         ab_track = []

#         known_powers = {}
#         def get_power(V_in):
#             try:
#                 return known_powers[V_in]
#             except KeyError:
#                 pass
#             vs = []
#             device.set_output_voltage(0,V_in)
#             for _ in range(m):
#                 v1 = float(device.get_input_value(1))
#                 v2 = float(device.get_input_value(2))
#                 vs.append((v1, v2))
#                 time.sleep(dt / 3)
#             vs = np.array(vs) * value_to_voltage
#             V1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
#             V2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1]))
#             P =  V1 * V2 * Voltage_multiplier / R_small
#             # known_powers[V_in] = P
#             ax1.errorbar(V_in, P.n, yerr=P.s, fmt='o')
#             return P.n

#         while b - a > optimized_threshold:
#             P_a = get_power(a)
#             P_b = get_power(b)
#             print(f"a = {a} (P = {P_a}), b = {b} (P = {P_b})")
#             ab_track.append((a,b))
#             if P_b > P_a: 
#                 a = (a + b) / 2
#             else:
#                 b = (a + b) / 2
#         ab_track = np.array(ab_track)
#         ax2.plot(ab_track[:,0])
#         ax2.plot(ab_track[:,1])
#         return (a + b) / 2


# class PVExperiment2(DiodeExperiment):
#     def __init__(self, port=None):
#         self.device = PreRecordedDevice(port=port)
#         self.device.set_output_voltage(0, 1.6)

#     def get_power(self, V_in=None, m=4, dt=0):
#         vs = []
#         if V_in is not None:
#             self.device.set_output_voltage(0, V_in)
#         for _ in range(m):
#             v1 = float(self.device.get_input_value(1))
#             v2 = float(self.device.get_input_value(2))
#             vs.append((v1, v2))
#             time.sleep(dt / 3)
#         vs = np.array(vs) * value_to_voltage
#         V1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
#         V2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1]))
#         P =  V1 * V2 * Voltage_multiplier / R_small
#         return P

#     def max_power(self, a=1.6, b=1.9, optimized_threshold=0.05, m=4, dt=0):
#         while b - a > optimized_threshold:
#             P_a = self.get_power(V_in=a, m=m, dt=dt).n
#             P_b = self.get_power(V_in=b, m=m, dt=dt).n
#             if P_b > P_a: 
#                 a = (a + b) / 2
#             else:
#                 b = (a + b) / 2

#         print(f"V_in = {(a + b) / 2}")
#         self.device.set_output_voltage(0, (a + b) / 2)

# class PVExperiment3(DiodeExperiment):
#     def __init__(self, port=None):
#         self.device = ArduinoVISADevice(port=port)
#         self.device.set_output_voltage(0, 1.6)

#     def get_power(self, V_in=None, m=4, dt=0):
#         vs = []
#         if V_in is not None:
#             self.device.set_output_voltage(channel=0, voltage=V_in)
#         for _ in range(m):
#             v1 = float(self.device.measure_input_value(channel=1))
#             v2 = float(self.device.measure_input_value(channel=2))
#             vs.append((v1, v2))
#             time.sleep(dt / 3)
#         vs = np.array(vs) * value_to_voltage
#         V1 = ufloat(np.mean(vs[:,0]), np.std(vs[:,0]))
#         V2 = ufloat(np.mean(vs[:,1]), np.std(vs[:,1]))
#         P =  V1 * V2 * Voltage_multiplier / R_small
#         return P

#     def max_power(self, a=1.6, b=1.9, optimized_threshold=0.05, m=4, dt=0):
#         while b - a > optimized_threshold:
#             P_a = self.get_power(V_in=a, m=m, dt=dt).n
#             P_b = self.get_power(V_in=b, m=m, dt=dt).n
#             if P_b > P_a: 
#                 a = (a + b) / 2
#             else:
#                 b = (a + b) / 2

#         print(f"V_in = {(a + b) / 2}")
#         self.device.set_output_voltage(0, (a + b) / 2)

