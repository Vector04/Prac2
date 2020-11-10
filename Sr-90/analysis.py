import numpy as np
import pandas as pd
from scipy import special
from matplotlib import pyplot as plt

from data_analysis_tools import *

# First, our data (I entered the data into an excel sheet)
df = pd.read_excel('data.xlsx')
df['sigma'] = np.sqrt(df['counts'])
print(df)

# there are two ways to determine sigma:
# Firstly, using the sqrt N method.
# Secondly, from the spread of counts variable. If the spread from the count variable is significanly larger than what sqrt N would predict, the intrinsics efficicies are different.

mean, std = np.mean(df['counts']), np.std(df['counts'])
stdmean = std / np.sqrt(6)

meanstd = np.mean(df['sigma'])

print(f"{mean=} \n{std=} \n{stdmean=} \n{meanstd=} \n")
# Note: the spread of counts (std) is greater than the poisson-predicted spread. (2 sigma)
# Attaching some numbers to this claim:
z = std / meanstd  # amount of sigma difference
p = special.erf(z)

print(f"{z=} \n{p=} \n")

# A baseline / average count and efficiency
bg = floatE(np.mean(df['background']), np.std(df['background']) / np.sqrt(6))
print(f"{bg=} \n")
avg_counts = floatE(mean, stdmean) - bg

# Given the counts, can we work backwards to find out the efficiency?
# (Errors are all 1 in the last decimal)
# The geometric efficiency:
e_g = (floatE(30, 1) / (floatE(150, 1) * 2))**2 / 4

# the true number of counts is A_real * delta t (both are given)
N_true = floatE(1400,1) * floatE(480, 1)
print(f"{e_g=} \n{N_true=}")

# We know that counts = n e_g e_i N_true <==> e_i = counts / (n e_g N_true)
# Sr --> Y --> Zr, n=2
e_i_avg = avg_counts / (2 * e_g * N_true)
print(f"{e_i_avg=}")
