from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize, integrate

from uncertainties import ufloat, unumpy, ufloat_fromstr


df = pd.read_csv('data.csv')
print(df)

# First, let us convert the masses to N_particles
molar_mass = 138.205
carbonate_mass = unumpy.uarray(
    df['carbonate_mass'].to_numpy(), [0.004] * 7)[1:]

moles = carbonate_mass / molar_mass

# For every mole of K2CO3, there are 2 K atoms.
moles_K = moles * 2

# Natural abunance of K is 1.17(1)×10−4
K_active_fraction = ufloat(1.17e-4, 1e-6)
moles_K_active = moles_K * K_active_fraction

# From moles to N particles.
N_A = 6.022e23
N_K_active = moles_K_active * N_A
print(f"{N_K_active = }")
print(dir(N_K_active))

# The geometric efficiency
# Note: The geomteric efficiency is dependant on the location of the decaying particle.
# This is why we integrate dx and use the mean value.


def e_geo(x, d=0):
    d = unumpy.nominal_values(d) / 2
    a = np.sqrt(x**2 + (2 - d) ** 2)
    if x < 8:
        c = np.sqrt(26**2 + 1)
        b = np.sqrt((3 - d)**2 + (26 - x)**2)
    else:
        c = 22
        b = np.sqrt((22 - x)**2 + (2 - d)**2)
    theta = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))
    return (1 - np.cos(theta / 2)) / 2


area = np.pi * ufloat(11, 0.1)**2 / 4
ds = carbonate_mass / (2.43 * area) * 100  # mm
e_gs = np.array(
    [ufloat(*integrate.quad(lambda x: e_geo(x, d), 0 , 11)) / 11 for d in ds])
print(f"{e_gs = }")

# The intrinsic efficiency, from the Sr-90 project
e_i_avg = ufloat(0.386, 0.029)


# Counts, as given
N_counts = unumpy.uarray(
    df['counts'] - 159, np.sqrt(df['counts']) + np.sqrt(159))[1:]

# Linear range correction, => lindracht.py
slope = ufloat(1364.8432519952598,86.66899838463745)
N_counts_rc = carbonate_mass * slope
print(f"{N_counts_rc = }")


n = 0.8928
# n = 1

taus = np.log(2) * N_K_active * ufloat(600,1) * n * e_i_avg * e_gs / N_counts
taus_rc = np.log(2) * N_K_active * ufloat(600,1) * \
    e_i_avg * e_gs * n / N_counts_rc


# From s to Gy
taus /= 31556926 * 1e9
taus_rc /= 31556926 * 1e9


# Plot of every datpoint
plt.errorbar(np.arange(1, 7,1), unumpy.nominal_values(
    taus), yerr=unumpy.std_devs(taus), label='Vanilla counts')
plt.errorbar(np.arange(1, 7,1), unumpy.nominal_values(
    taus_rc), yerr=unumpy.std_devs(taus_rc), label='RC counts')


plt.xlabel('Datapoint')
plt.ylabel(r'$\tau_{1/2} (Gy)$')
plt.legend(loc=2)
plt.grid()
plt.show()
plt.savefig("datapoints.png")
print(f"Tau: {np.mean(taus_rc) } Gy")
