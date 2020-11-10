from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize

from uncertainties import ufloat, unumpy


df = pd.read_csv('data.csv')
print(df)

# First, let us convert thes masses to N_particles
molar_mass = 138.2
carbonate_mass = unumpy.uarray(
    df['carbonate_mass'].to_numpy(), [0] + [0.004] * 6)

moles = carbonate_mass / molar_mass

# For every mole of K2CO3, there are 2 unstable  K particles.
moles_K = moles * 2

# Natural abunance of K is 1.17(1)×10−4
K_active_fraction = ufloat(1.17e-4, 1e-6)
# np.sqrt((self.val * a.error)**2 + (a.val * self.error)**2))
moles_K_active = moles_K * K_active_fraction

N_A = 6.022e23
N_K_active = moles_K_active * N_A
print(f"{N_K_active = }")

# The geometric efficiency
d_det = ufloat(3, 0.1)
r = (ufloat(15, 0.05)**2 + d_det**2)**0.5
print(f"{r = }")
h = r - d_det
e_g = h / (2 * r)
print(f"{e_g = }")

# The intrinsic efficiency, from the Sr-90 project
e_i_avg = ufloat(0.386, 0.029)


N_counts = unumpy.uarray(df['counts'] - 159, np.sqrt(df['counts']))[1:]
# Counts, range_corrected (rc)
df2 = pd.read_csv('data2.csv')
N_counts_rc = df2['counts (RC)'].to_numpy()
print(f"{N_counts_rc = }")

N_actives = N_K_active[1:]


taus = np.log(2) * N_actives * ufloat(600,1) / (e_i_avg * e_g * N_counts)
taus_rc = np.log(2) * N_actives * ufloat(600,1) / (e_i_avg * e_g * N_counts_rc)
print(dir(taus))


plt.plot(unumpy.nominal_values(N_actives / N_counts))

# plt.plot(unumpy.nominal_values(taus / 31556926))
# plt.plot(unumpy.nominal_values(taus_rc / 31556926))
plt.show()
print(taus)
