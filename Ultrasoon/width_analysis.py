


import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
from lmfit import models, Parameter, Parameters


folder_to_distance = {
    "meting13/": 1,
    "meting14/": 2,
    "meting15/": 3,
    "meting16/": 4,
    "meting17/": 5,
    "meting18/": 5,
    "meting19/": 1.1,
    "meting20/": 2.1,
    "meting21/": 0,
    "meting24/": 0,
}

folder_to_x_end = {
    "meting13/": 75,
    "meting14/": 75,
    "meting15/": 75,
    "meting16/": 75,
    "meting17/": 75,
    "meting18/": 75,
    "meting19/": 73,
    "meting20/": 73,
    "meting21/": 73,
    "meting24/": 70,
}

fig, ax = plt.subplots()

folder = "meting23/"

def plot_chart(folder, fig, ax):


    df = pd.read_csv(folder + "data.csv")
    df.drop(["Unnamed: 0", "t"], axis=1, inplace=True)

    xs = sorted(df.columns)
    

    ys = [sum(df[x]) for x in xs]

    xs = [float(x) for x in xs]

    x_start, x_end = min(xs), max(xs)
    stepsize = xs[1] - xs[0]

    ax.scatter(xs[2:-2], ys[2:-2], label=folder[:-1])

    # Now, some analysis. 
    # The first order of business is to determine the std on the reflection
    # On where x < 64 mm
    xs, ys = np.array(xs), np.array(ys)
    ys_base = ys[np.where(xs < 62)]
    base_mean = np.mean(ys_base)
    base_std = np.std(ys_base)
    # print(base_mean, base_std)

    y_min = min(ys)

    # Victor Coëfficiënt
    c_v = (base_mean - y_min) / base_std

    # ax.scatter(folder_to_distance[folder], c_v, label="first", c="violet")

    # print(folder_to_distance[folder], c_v)

    # Moreover, we would like to determine the width of all peaks. We do this by fitting a special gaus funtion.

    # def f(x, sigma, amp, mu, base):
    #     return base - amp * np.exp(-((x - mu) / sigma)**2 / 2)

    # gmodel = models.Model(f)
    
    # params = Parameters()
    # params.add_many(('sigma', 0.4, True, 1), ('amp', 3000, True, 1), (
    #                 'mu', 67, True, 1), ('base', base_mean, True, 1))
    # # Properly selected data
    # selector = np.where(xs < folder_to_x_end[folder])
    # xs_fit = xs[selector]
    # ys_fit = ys[selector]
    # fit_result = gmodel.fit(ys_fit, params=params, x=xs_fit)
    # print(folder, folder_to_distance[folder], fit_result.best_values, fit_result.redchi)
    # fit_result.plot_fit()
    # print()


    # This works very poorly, we switch to a half-width half max approach.
    mu = xs[ys.argmin()]

    half_height = (base_mean + y_min) / 2

    # Some smart numpy tricks
    index_hw = np.abs(ys - half_height).argmin()
    x_hw = xs[index_hw]

    sigma = x_hw - mu
    ax.scatter(x_hw, half_height)
    # ax.plot(xs, np.abs(ys - half_height))
    # print(mu, x_hw, index_hw)
    print(folder_to_distance[folder], sigma)







    

plot_chart("meting24/", fig, ax)

for n in range(14, 25):
    plot_chart(f"meting{n}/", fig, ax)

# plot_chart(f"meting17/", fig, ax)

plt.legend()
plt.show()