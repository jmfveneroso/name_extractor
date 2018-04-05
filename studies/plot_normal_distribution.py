#!/usr/bin/env python
# -*- coding: utf-8 -*-

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Computer Modern']})
rc('text', usetex=True)
import matplotlib.pyplot as plt
import numpy as np
import math

mean = 0
variance = 1

# Figure 1.
x = np.arange(-3.0, 3.1, 0.1)

def normal(x):
  expoent = -((x - mean)**2) / (2 * variance);
  a = 1 / math.sqrt(2 * math.pi * variance)
  return a * math.exp(expoent)

normal = np.vectorize(normal)
y = normal(x)

plt.plot(x, y)
# plt.xlim(-1, 1)
# plt.ylim(-1, 1)
# 
# plt.xticks(x, ['', '', '', '', '0', 'x', r'x + $\Delta$x', '', ''])
# plt.yticks(x, ['', '', '', '', '0', 'y', r'y + $\Delta$y', '', ''])
# 
# plt.axvline(x=0)
# plt.axhline(y=0)
# 
# p = plt.axhspan(0.25, 0.5, facecolor='0.5', alpha=0.5)
# p = plt.axvspan(0.25, 0.5, facecolor='0.5', alpha=0.5)

plt.title(r'Figure 2')
plt.grid(linestyle='dotted')

# plt.show()
plt.savefig('figure_2.png')
