from data_analysis_tools import *

dt1 = floatE(0.011, 1e-3) * 1e-3
L1 = 2 * floatE(15, 1) * 1e-3

print(f"v = {L1 / dt1}")

dt2 = floatE(0.0192, 0.0010) * 1e-3
L2 = 2 * floatE(28, 1) * 1e-3

print(f"v = {L2 / dt1}")