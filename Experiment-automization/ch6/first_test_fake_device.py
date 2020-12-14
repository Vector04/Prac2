from pythonlab.controllers.prerecorded_device import PreRecordedDevice
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import time
from os import listdir
from os.path import join, splitext

from uncertainties import ufloat, unumpy


device = PreRecordedDevice()
print(device.get_identification())


# We vary U0, observe what happens to U1 and U2.

n, m = 20, 10

V_ins = np.linspace(1.65, 1.85, n)
# V_ins = np.linspace(0, 3.3, n)
v1s = np.empty((n,m))
v2s = np.empty((n,m))



for i,V_in in enumerate(V_ins):
    device.set_output_value(value=int(V_in / 3.3 * 1023), channel=0)
    # time.sleep(0.2)

    for ii in range(m):
        v1s[i, ii] = device.get_input_value(1)
        v2s[i, ii] = device.get_input_value(2)
        # time.sleep(0.05)


    print(i, end=", ")
print()


device.set_output_voltage(0, 0)

v1s *= 3.3 / 1023  
v2s *= 3.3 / 1023  

print(V_ins)
print(v1s)
print(v2s)


# V_cell = 3 V1
# I_cell = \frac{U_2(3 M \Ohm + R_v)}{4.7 \cdot 3m\Ohm}

# V_cells = 3 * unumpy.uarray(np.mean(v1s, axis=1, np.std(v1s, axis=1))
def meanstd(x):
    return np.mean(x, axis=1), np.std(x, axis=1)
v1s, dv1s = meanstd(v1s)
v2s, dv2s = meanstd(v2s)


plt.errorbar(V_ins, v1s, yerr=dv1s, label='Channel 1')
plt.errorbar(V_ins, v2s, yerr=dv2s, label='Channel 2')
plt.xlabel("V_in (Ch0) (V)")
plt.ylabel("V_out (Ch1&2) (V)")

plt.legend()
plt.ylim((0, 3.3))
pd.DataFrame({"V_0": V_ins, "V_1": v1s, "dV_1": dv1s, "V_2": v2s, "dV_2": dv2s}).to_csv("data_fake.csv", index=False)

# plt.savefig("Scan with std devs.png")
plt.show()

