import numpy as np 
import pandas as pd 
from matplotlib import pyplot as plt 
from uncertainties import ufloat, unumpy


df = pd.read_csv("data.csv")
print(df)