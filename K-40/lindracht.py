from data_analysis_tools import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize
from uncertainties import ufloat, unumpy, ufloat_fromstr

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.sans-serif": ["Computer Modern Roman"],
    "font.size": 12,
    "font.weight": 600,
})

# Parsing original data
df = pd.read_csv('data.csv')

masses = unumpy.uarray(df.iloc[1:, 0].to_numpy(), 0.004)
counts = unumpy.uarray(df.iloc[1:, 1] - 159,
                       np.sqrt(df.iloc[1:, 1]) + np.sqrt(159))

plt.errorbar(unumpy.nominal_values(masses), unumpy.nominal_values(counts),
             yerr=unumpy.std_devs(counts),fmt='o', label="Meetpunten (exclusief achtergrond)", ms=4)

# Chosing our data to be used for the linfit:
# the origin, the first, second and third datapoint
xs = unumpy.nominal_values(np.append([0], masses[0:3]))
ys = unumpy.nominal_values(np.append([0], counts[0:3]))
sigma = unumpy.std_devs(np.append([ufloat(0, 10)], counts[0:3]))


def lin(x, a):
    return a * x


popt, pcov = optimize.curve_fit(lin, xs, ys, sigma=sigma, p0=(1000))

params = unumpy.uarray(popt, np.sqrt(np.diag(pcov)))
chi2 = chi_squared(lambda x: lin(x, *popt), xs, ys, sigma)

print(f"alpha: {params[0]}")
print(f"{chi2 = }")
# Plot
ms = np.linspace(0, 1.4, 10)
plt.plot(ms, lin(ms, *popt), label="Fit van geselecteerde meetpunten")
plt.errorbar(xs, ys, yerr=sigma, fmt='o', ms=5,
             label="Geselecteerde meetpunten")

plt.title("Counts, met drachtcorrectie", fontsize=20, fontweight=1000)
plt.xlabel("Carbonaatmassa (g)", fontsize=14)
plt.ylabel("Counts", fontsize=14)
plt.grid()
plt.legend()

plt.savefig("Range_correction.png")
plt.show()
