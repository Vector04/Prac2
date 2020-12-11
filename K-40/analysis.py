from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize, integrate, stats

from uncertainties import ufloat, unumpy, ufloat_fromstr


df = pd.read_csv('data.csv')
print(df)

# First, let us convert the masses to N_particles
molar_mass = 138.205
carbonate_mass = unumpy.uarray(
    df['carbonate_mass'].to_numpy(), [0.004] * 7)[1:]

for x in carbonate_mass:
    x.tag = "mass"

moles = carbonate_mass / molar_mass

# For every mole of K2CO3, there are 2 K atoms.
moles_K = moles * 2

# Natural abunance of K is 1.17(1)×10−4
K_active_fraction = ufloat(1.17e-4, 1e-6, tag="f_active")
moles_K_active = moles_K * K_active_fraction

# From moles to N particles.
N_A = 6.022e23
N_K_active = moles_K_active * N_A
print(f"{N_K_active = }")

# The geometric efficiency
# Note: The geomteric efficiency is dependant on the location of the decaying particle.
# This is why we integrate dx and use the mean value.


def e_geo(x, d=0):
    d /= 2
    a = unumpy.sqrt(x**2 + (2 - d) ** 2)
    # Look at geometric_efficiency.png to see what these mean
    h1 = ufloat(2,0.1)
    h2 = ufloat(3,0.1)
    w1 = ufloat(22, 0.1)
    w2 = ufloat(30, 0.1)

    if x < 8:
        c = unumpy.sqrt(((w1 + w2) / 2)**2 + (h2 - h1)**2)
        b = unumpy.sqrt((h2 - d)**2 + ((w1 + w2) / 2 - x)**2)
    else:
        c = w1
        b = unumpy.sqrt((w1 - x)**2 + (h1 - d)**2)
    theta = unumpy.arccos((a**2 + b**2 - c**2) / (2 * a * b))
    return (1 - unumpy.cos(theta / 2)) / 2


area = np.pi * ufloat(11, 0.1)**2 / 4
ds = carbonate_mass / (2.43 * area) * 100  # mm
e_gs = [0] * 6

ntries = 1000
for i, d in enumerate(ds):
    # Integrate
    xs = np.linspace(0, 11, ntries)
    e_g = sum([e_geo(x, d=d) * 11 / ntries for x in xs]) / 11
    e_gs[i] = ufloat(e_g.n, e_g.s, tag="e_g")
    print(e_g)
print(f"{e_gs}")

# The intrinsic efficiency, from the Sr-90 project
e_i_avg = ufloat(0.386, 0.029, tag="e_i")
print(f"{e_i_avg = }")

# Counts, as given
N_counts = unumpy.uarray(
    df['counts'] - 159, np.sqrt(df['counts']) + np.sqrt(159))[1:]

for x in N_counts:
    x.tag = "N_c"


# Linear range correction, => lindracht.py
slope = ufloat(1342.2511926817513, 61.0286551244589, tag="alpha")

N_counts_rc = carbonate_mass * slope

print(f"{N_counts = }")
print(f"{N_counts_rc = }")

n = ufloat(0.8928, 0.001, tag="n")
delta_t = ufloat(600, 1, tag="dt")


taus = np.log(2) * N_K_active * delta_t * n * e_i_avg * e_gs / N_counts
taus_rc = np.log(2) * N_K_active * delta_t * \
    e_i_avg * e_gs * n / N_counts_rc


# From s to Gy
taus /= 31556926 * 1e9
taus_rc /= 31556926 * 1e9

print(f"{taus_rc = }")
# Printing results
print(f"Tau: {np.mean(taus_rc) } Gy")

# composition of error on tau
total = 0
print("Variable    std dtau_component")
for (var, error) in sorted(taus_rc[0].error_components().items(), key=lambda x: x[1], reverse=True):
    print(f"{str(var.tag).rjust(8)} {str(round(var.s, 3)).rjust(6)} {error}")
    total += error**2

# Plot of every datapoint
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.sans-serif": ["Computer Modern Roman"],
    "font.size": 12,
    "font.weight": 600,
})

plt.errorbar(df['carbonate_mass'][1:], unumpy.nominal_values(
    taus), yerr=unumpy.std_devs(taus), label='Vanilla counts', c='#0377fc')
plt.errorbar(df['carbonate_mass'][1:], unumpy.nominal_values(
    taus_rc), yerr=unumpy.std_devs(taus_rc),
    label='Drachtsgecorigeerde counts', c='#fca103')

plt.title("Halfwaardetijden", fontsize=20, fontweight=1000)
plt.xlabel('Datapunt massa (g)', fontsize=14)
plt.ylabel(r'$\tau_{1/2} (Gy)$', fontsize=14)
plt.legend(loc=2)
plt.grid()
plt.show()
plt.savefig("datapunten_tau.png")
