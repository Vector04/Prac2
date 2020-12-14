import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
from lmfit import models, Parameter, Parameters


columns = ["index"] + [f"{x:.2f}" for x in np.arange(40, 120.1, 0.2)] + ["t"]
df = pd.read_csv("meting24/" + "data.csv", names=columns)


# xs = sorted(df.columns)
df.drop(["index", "t"], axis=1, inplace=True)



xs = df.columns
ys = np.array([sum(df.loc[200:700, x]) for x in xs])

xs_float = np.array([float(x) for x in xs])

fig, (ax1, ax2) = plt.subplots(ncols=2)
ax2.plot(xs_float, ys)
# ticks = np.arange(0, 121, 20)
# ax.set_xticks(ticks)

ax1.imshow(df)
ax1.set_aspect(0.1)
ax2.set_aspect(0.015)



ys_base = ys[xs_float < 75]
base_mean = np.mean(ys_base)
base_std = np.std(ys_base)
print("Base mean and std:", base_mean, base_std)

y_min = min(ys)

# Victor Coëfficiënt
c_v = (base_mean - y_min) / base_std
print("Vector Coëfficiënt:", c_v)

mu = xs_float[ys.argmin()]

half_height = (base_mean + y_min) / 2

# Some smart numpy tricks
index_hw = np.abs(ys - half_height).argmin()
x_hw = xs_float[index_hw]

sigma = x_hw - mu

print("sigma:", sigma)
ax2.scatter(x_hw, half_height)



plt.show()