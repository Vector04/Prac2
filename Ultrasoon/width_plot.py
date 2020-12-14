import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal

# plt.style.use("grayscale")



fig, ax = plt.subplots()
ax.scatter([2,3,4,5,5], [1,2.5,2.5,3.5,3.5], s=50, c="k", marker='^', label="Series 1, stepsize = 0.5 mm")
ax.scatter([0,1,2], [1,1.2, 1.4], c="k", s=20, marker='o', label="Series 2, stepsize = 0.2 mm")

ax.set_xlabel("d (mm)")
ax.set_ylabel(r"$\sigma$ [half-width-half-max] mm")
ax.set_title("Block distance vs sigma")
ax.set_ylim(bottom=0)
plt.legend()

plt.savefig("Distance-Sigma.png")
plt.show()
