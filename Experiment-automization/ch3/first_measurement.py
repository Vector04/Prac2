import pyvisa
import numpy as np
import time
from matplotlib import pyplot as plt
import pandas as pd
from os import listdir
from os.path import isfile, join, splitext


rm = pyvisa.ResourceManager("@py")
ports = rm.list_resources()
print(ports)

device = rm.open_resource(
    ports[-1], read_termination="\r\n", write_termination="\n")

# print(device.query("*IDN?"))

# print(device.query("OUT:CH0 480"))
print(device.query("MEAS:CH0:VOLT?"))
# print(device.query("MEAS:CH1:VOLT?"))
# print(device.query("MEAS:CH2:VOLT?"))


voltage_values_bit = np.arange(0, 1023, 50)
v_outs1, v_outs2 = [], []

for voltage in voltage_values_bit:
    device.query(f"OUT:CH0 {voltage}")
    v_out1 = float(device.query("MEAS:CH1:VOLT?"))
    v_out2 = float(device.query("MEAS:CH2:VOLT?"))
    v_outs1.append(v_out1)
    v_outs2.append(v_out2)
    time.sleep(0.2)

device.query(f"OUT:CH0 0")
device.close()

v_ins = 3.3 * voltage_values_bit / 2**10
print(v_ins)
print(v_outs1)
print(v_outs2)

df = pd.DataFrame({'V_in': v_ins, 'V_out1': v_outs1, 'V_out2': v_outs2})

def save_csv(df):
    # Saving the file to a unique txt, quite the pain:
    try:
        open('test_results_001.csv')
    except FileNotFoundError:
        df.to_csv('test_results_001.csv')
    else: 
        file_number = max([int(splitext(file)[0][-3:]) for file in listdir() if splitext(file)[1] == '.csv'] ) + 1
        df.to_csv(f"test_results_{str(file_number).zfill(3)}.csv")

# Saving the file to hdf5:
def save_hdf(df):
    with pd.HDFStore('test_results.h5') as hdf:
        keys = hdf.keys()
    # Smart trick to create unique keys
    df.to_hdf('test_results.h5', key=f'test_result{str(len(keys)).zfill(3)}', mode='a')

save_hdf(df)

plt.plot(v_ins, np.array(v_outs1), label='ch1')
plt.plot(v_ins, np.array(v_outs2), label='ch2')
plt.grid()
plt.legend()
plt.xlabel('V_in (V)')
plt.ylabel('V_out (V)')
plt.title('Spanningsverloop', fontsize=13)
plt.savefig('3.2-grafiek.png')
plt.show()
