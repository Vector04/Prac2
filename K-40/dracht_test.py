from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize
from uncertainties import ufloat, unumpy, ufloat_fromstr


df = pd.read_csv('data2.csv', converters={
    'counts (RC)': ufloat_fromstr, 'carbonate_mass': ufloat_fromstr})

xs = unumpy.nominal_values(df['carbonate_mass'].to_numpy())
_ys = df['counts (RC)'].to_numpy()
ys = unumpy.nominal_values(_ys)
sigma = unumpy.std_devs(_ys)
print(ys.dtype)


def f(x, a, b):
    return a * x + b


popt, pcov = optimize.curve_fit(f, xs, ys, sigma=sigma)
chi2 = chi_squared(lambda x: f(x, *popt), xs, ys, sigma)

params = unumpy.uarray(popt, np.sqrt(np.diag(pcov)))

print(params)
print(chi2)

plt.errorbar(xs, ys, yerr=sigma, label='RC Counts')
plt.plot(xs, f(xs, *popt), label='Fit of RC Counts')
df_orig = pd.read_csv('data.csv')
data_orig = df_orig[['carbonate_mass', 'counts']].to_numpy()
plt.plot(df_orig['carbonate_mass'], df_orig['counts'], label='Counts')

print(data_orig)

# another crazy idea: assume there is no range loss in the first two points, then:
x1, y1 = unumpy.uarray(data_orig[1], (0.004, np.sqrt(data_orig[1,1])))
x2, y2 = unumpy.uarray(data_orig[3], (0.004, np.sqrt(data_orig[3,1])))
slope = (data_orig[3,1] - data_orig[1, 1]) / (data_orig[3,0] - data_orig[1, 0])
shift = data_orig[1]

print(slope, shift)
print(repr((y2 - y1) / (x2 - x1)))


def f2(x):
    return slope * (x - shift[0]) + shift[1]


print(f"f0: {f2(0)}")
plt.plot(data_orig[:,0], f2(data_orig[:,0]),
         label='Line through first 2 points')
plt.legend(loc=2)
plt.show()
