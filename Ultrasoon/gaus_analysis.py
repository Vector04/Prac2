import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
from lmfit import models, Parameter, Parameters
import click


# folder = 'meting3/'
fig, ax = plt.subplots()


def make_gauss(folder):

    df = pd.read_csv(folder + "data.csv")
    print(df)
    # print(df['20.0'])
    df.drop(["Unnamed: 0", "t"], axis=1, inplace=True)

    # print(df)

    xs = np.array([float(x) for x in df.columns])
    ys = np.array([sum(df[x]) for x in df.columns])

    def f(x, sigma, amp, mu, base):
        return base + amp * np.exp(-((x - mu) / sigma)**2 / 2)

    gmodel = models.Model(f)
    # params = gmodel.guess(ys, x=xs)
    params = Parameters()
    params.add_many(('sigma', 5, True, 1), ('amp', 1000, True, 1), (
                    'mu', 35, True, 1), ('base', 200, True, 1))
    fit_result = gmodel.fit(ys, params=params, x=xs)
    print(folder)
    print(fit_result.fit_report())
    print()

    ax.plot(xs, ys, label=folder[:-1])
    ax.plot(xs, fit_result.eval(), label=folder[:-1] + 'fit')


if __name__ == '__main__':
    make_gauss("meting7/")
    make_gauss("meting8/")
    make_gauss("meting9/")
    plt.legend()
    plt.show()
