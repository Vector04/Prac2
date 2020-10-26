import numpy as np
from matplotlib import pyplot as plt
from scipy import optimize
import pandas as pd
import inspect

import floats
from helpers import *


def better_curve_fit(f, xdata, ydata, p0=None, sigma=None, **kwargs):
    """
    A modified version of curve_fit which returns more useful information.

    """
    global popt
    popt, pcov = optimize.curve_fit(
        f, xdata, ydata, p0=p0, sigma=sigma, **kwargs)
    argspec = inspect.getfullargspec(f)
    params = ParamDict({param: floats.floatE(val, error)
                        for param, val, error in zip(argspec[0][1:], popt, np.sqrt(np.diag(pcov)))})
    if sigma.any():
        chi2 = chi_squared(lambda x: f(x, *popt), xdata, ydata,
                           sigma) / (len(xdata - len(popt)))
        return params, chi2
    return params


pd.options.display.max_rows = 999


# Reading data
df = pd.read_csv('data.csv')
# print(df)

# Some cutting / processing
# Splitting datasets into background and decay data
data_set_1 = (df.loc[:10, ['t', 'N1']], df.loc[12:, ['t', 'N1']])
data_set_2 = (df.loc[:12, ['t', 'N2']], df.loc[13:, ['t', 'N2']])
data_set_3 = (df.loc[:12, ['t', 'N3']], df.loc[13:, ['t', 'N3']])

# Creating Figures and axes for plotting
fig, axs = plt.subplots(ncols=2, nrows=2, figsize=(7.68,5.88))

# Analysing the 3 datasets
half_times = []

for i, ((bg_data, decay_data), ax) in enumerate(zip([data_set_1, data_set_2, data_set_3], axs.flatten()[:3])):

    # First, the background noise
    def meanstd(ar):
        return np.mean(ar), np.std(ar)
    bg, dbg = meanstd(bg_data[bg_data.columns[1]])

    # Now, we want to fit the decay curve

    def f(t, lamda, N0, bg):
        return N0 * np.exp(-lamda * t) + bg

    Ns = decay_data[decay_data.columns[1]]
    params, chi2 = better_curve_fit(f, decay_data['t'], Ns , p0=(
        0.01, 1000, bg), sigma=np.sqrt(Ns))

    # Parameters
    lamda = params['lamda']
    N0 = params['N0']
    bg_fit = params['bg']
    t_12 = np.log(2) / params['lamda']
    half_times.append(t_12)

    # Printing Fit results
    print(f"Series {i +1}:")
    print("Avg Background:", floats.floatE(bg,dbg))
    print(params)
    print(f"{chi2=}")
    print(f"Half-time: {t_12}")
    print()
    # Plotting
    ax.errorbar(decay_data['t'], Ns, np.sqrt(Ns), fmt='o', ms=3, label='Data')
    ax.plot(decay_data['t'], f(decay_data['t'],
                               lamda.val, N0.val, bg_fit.val), label='Fit')
    # Plot Formatting
    ax.set_xticks(np.arange(0, 601, 100))
    ax.set_ylim((0, 350))
    ax.set_xlabel(r't ($s$)')
    ax.set_ylabel('Counts')
    ax.set_title(f'Serie {i+1}')
    ax.legend()
    ax.grid()


axs[1, 1].axis('off')
fig.suptitle('Verval Rn-220', fontsize=16, y=1)
plt.tight_layout()
plt.savefig('Verval.png')
plt.show()


# Average of the 3 half-times
T_12 = sum(half_times) / 3
print(f"Average Half-time: {T_12}")
