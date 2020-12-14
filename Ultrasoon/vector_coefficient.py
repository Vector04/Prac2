import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal

# Proper plotting of Vector Coefficient, determined in width_analysis.py

fig, ax = plt.subplots()

ax.scatter([1,2,3,4,5,5], [28.23403966758035,70.07026379616376,92.20755270258934,119.75774119213081,104.04394207386198,103.3117400619845], label="Series 1, stepsize = 0.5 mm", c="k", marker='^', s=50)

ax.scatter([0,1,2], [67.54438338658747, 124.13208104042766, 100.28727041898854], label="Series 2, stepsize = 0.2 mm", c="k", marker='o', s=20)

ax.set_title("Vector Coëfficiënt")
ax.set_xlabel("distance between blocks (mm)")
ax.set_ylabel(r"$C_v$ [dimensionless]")
plt.legend()


plt.savefig("Vector Coëfficiënt plot.png")



plt.show()