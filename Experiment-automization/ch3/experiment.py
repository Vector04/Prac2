from pythonlab.controllers.arduino_device import ArduinoVISADevice
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import time
from os import listdir
from os.path import join, splitext

# Creating device
device = ArduinoVISADevice()
print(device.get_hardware_info())
# print(device.query("OUT:CH1:VOLT?"))

# Input voltage values
v_ins = np.linspace(0, 3.3, 15)
v_outs1, v_outs2 = [], []

# Measuring output voltages
for voltage in v_ins:
    device.set_output_voltage(channel=0, voltage=voltage)
    v_out1 = device.measure_input_voltage(channel=1)
    v_out2 = device.measure_input_voltage(channel=2)
    v_outs1.append(v_out1)
    v_outs2.append(v_out2)
    time.sleep(0.2)

# Shutting down led
device.set_output_voltage(channel=0, voltage=0)

# Data to pandas dataframe
df = pd.DataFrame({'V_in': v_ins, 'V_out1': v_outs1, 'V_out2': v_outs2})
print(df)


def save_csv(df):
    # Saving the file to a unique txt file, quite the pain:
    try:
        open('test_results_001.csv')
    except FileNotFoundError:
        df.to_csv('test_results_001.csv')
    else:
        file_number = max([int(splitext(file)[0][-3:])
                           for file in listdir() if splitext(file)[1] == '.csv']) + 1
        df.to_csv(f"test_results_{str(file_number).zfill(3)}.csv")

# Saving the data to an hdf5 file:


def save_hdf(df):
    # Saving the data to the hdf5 file is easier
    with pd.HDFStore('test_results.h5') as hdf:
        keys = hdf.keys()
    # Smart trick to create unique keys
    df.to_hdf('test_results.h5',
              key=f'test_result{str(len(keys)).zfill(3)}', mode='a')


save_csv(df)

# Plotting our data
plt.plot(v_ins, np.array(v_outs1), label='ch1')
plt.plot(v_ins, np.array(v_outs2), label='ch2')
plt.grid()
plt.legend()
plt.xlabel(r'$V_{in}$ (V)')
plt.ylabel(r'$V_{out}$ (V)')
plt.title('Spanningsverloop', fontsize=13)
# Saving figure
plt.savefig('3.2-grafiek.png')
plt.show()
