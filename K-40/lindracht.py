from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize
from uncertainties import ufloat, unumpy, ufloat_fromstr


df = pd.read_csv('data.csv')

masses = unumpy.uarray(df.iloc[1:, 0].to_numpy(), 0.004)
counts = unumpy.uarray(df.iloc[1:, 1] - 159,
                       np.sqrt(df.iloc[1:, 1]) + np.sqrt(159))

plt.plot(unumpy.nominal_values(masses), unumpy.nominal_values(counts))
# plt.xlim(left=0)
# plt.ylim(bottom=0)
# plt.show()

# Chosing our data to be used for the linfit:
# the origin, the first and third point
xs = unumpy.nominal_values(np.append([0], masses[0:3:2]))
ys = unumpy.nominal_values(np.append([0], counts[0:3:2]))
sigma = unumpy.std_devs(np.append([ufloat(0, 10)], counts[0:3:2]))


def lin(x, a):
    return a * x


popt, pcov = optimize.curve_fit(lin, xs, ys, sigma=sigma, p0=(1000))

params = unumpy.uarray(popt, np.sqrt(np.diag(pcov)))
chi2 = chi_squared(lambda x: lin(x, *popt), xs, ys, sigma)

print(params)
print(chi2)
ms = np.linspace(0, 1.4, 10)
plt.plot(ms, lin(ms, *popt))
plt.errorbar(xs, ys, yerr=sigma, fmt='o', ms=2)
plt.show()
