from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize
from uncertainties import ufloat, unumpy


df = pd.read_csv('data.csv')
print(df)

carbonate_density = 2.43
masses = unumpy.uarray(df.iloc[1:, 0].to_numpy(), 0.004)
print(masses)
volumes = masses / carbonate_density
thickness = volumes
counts = df.iloc[1:, 1] - 159
# print(counts)

# sigmas = np.sqrt(df['counts']).iloc[1:,]

# plt.errorbar(masses, counts, yerr=sigmas, label='counts')
# plt.errorbar(masses, counts / masses, yerr=sigmas /
#              masses, label='counts per mass')


# def p(mass, Eff, a):
#     d = np.cbrt(mass / carbonate_density)
#     return Eff * (1 - np.exp(-a * d)) / (a * d)


# # plt.plot(df['carbonate_mass'], p(
# #     df['carbonate_mass'], 12000, 20), label='base_fit')


# popt, pcov = optimize.curve_fit(
#     p, masses, counts / masses, sigma=sigmas / masses, p0=(12000, 20))

# print(f"{popt = }")
# print(f"{pcov = }")


# plt.plot(df['carbonate_mass'], p(df['carbonate_mass'], *popt),
#          label='fit of counts/mass')
# plt.plot(masses, masses * p(masses, * popt), label='counts, range corrected')

# plt.xlabel('mass (g)')
# plt.ylabel('counts, counts/mass')
# plt.legend()
# plt.show()

# # params =

# df2 = pd.DataFrame(
#     {'carbonate_mass': masses, 'counts (RC)': masses * p(masses, *popt)})
# df2.to_csv('data2.csv')


# params, chi2 = better_curve_fit(
#     p, df['carbonate_mass'], df['counts'] - 159, sigma=np.sqrt(df['counts']), p0=(10000, 10))

# print(params)
# print(f"{chi2 = }")
# a, b = params['a'], params['b']
# corr_power = params['b'].val

# plt.plot(df['carbonate_mass'], p(
#     df['carbonate_mass'], a.val, b.val), label='fit')
# plt.plot(masses, counts * masses**(-1 * corr_power), label='power_corrected')

# plt.legend()
# plt.show()
