from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize
from uncertainties import ufloat, unumpy


df = pd.read_csv('data.csv')
print(df)

# Preparing our data
masses = unumpy.uarray(df.iloc[1:, 0].to_numpy(), 0.004)
counts = unumpy.uarray(df.iloc[1:, 1] - 159,
                       np.sqrt(df.iloc[1:, 1]) + np.sqrt(159))
counts_per_m = counts / masses
print(counts_per_m)


def p(d, Eff, a):
    return Eff * (1 - np.exp(-a * d)) / (a * d)


xdata = unumpy.nominal_values(masses)
ydata = unumpy.nominal_values(counts_per_m)
sigma = unumpy.std_devs(counts_per_m)

print(f"{xdata = }")
print(f"{ydata = }")
print(f"{sigma = }")

popt, pcov = optimize.curve_fit(p, xdata, ydata, sigma=sigma)

params = unumpy.uarray(popt, np.sqrt(np.diag(pcov)))
chi2 = chi_squared(lambda d: p(d, *popt), xdata, ydata, sigma)

print(f"{params = }")
print(f"{chi2 = }")

ms1 = np.linspace(0.001, 1.05 * max(xdata), 10)

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(13, 4.2))
ax1.plot(ms1, p(
    ms1, *popt), label='fit of counts/m')

ax1.errorbar(xdata, ydata, yerr=sigma, fmt='o', label='counts/m')
ax1.legend()
ax1.set_title("Counts per mass")


# plt.plot(unumpy.nominal_values(thickness), counts /
#          (unumpy.nominal_values(thickness) * count0), label='counts/d')

ms = unumpy.nominal_values(masses)

# For proper error propagation we need to create a ufloat-supported version of p(d, eff, a):


def p2(d, Eff, a):
    return Eff * (1 - unumpy.exp(-a * d)) / (a * d)


counts_rc = params[0] * counts / p2(masses, *params)
print(p2(masses, *params) / params[0])
print(f"{counts_rc = }")
ax2.plot(ms, unumpy.nominal_values(counts), label='counts')
ax2.plot(ms, unumpy.nominal_values(counts_rc), label='counts, rc')

ax2.legend()
ax2.set_title("Counts")

ax3.plot(ms1, p(ms1, *popt) / popt[0], label='Fit')
ax3.scatter(ms, ydata / popt[0], label='data', c='C1')

ax3.scatter(ms, ydata / p(ms, *popt), label='rc counts, normalized')

print(p(ms[0], *popt / ydata[0]))

ax3.legend()
ax3.set_title("Counts per mass, normalized")

ax1.set_xlim(left=0)
ax2.set_xlim(left=0)
ax3.set_xlim(left=0)
ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)
ax3.set_ylim(bottom=0)

ax1.set_xlabel('Mass (g)')
ax2.set_xlabel('Mass (g)')
ax3.set_xlabel('Mass (g)')
ax1.grid()
ax2.grid()
ax3.grid()

plt.tight_layout()
plt.show()

df2 = pd.DataFrame(
    {'carbonate_mass': masses, 'counts (RC)': counts_rc})
df2.to_csv('data2.csv')
