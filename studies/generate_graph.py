#!/usr/bin/env python
# -*- coding: utf-8 -*-

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Computer Modern']})
rc('text', usetex=True)
import matplotlib.pyplot as plt
import numpy as np

# Figure 1.
x = np.array([ -1, -0.75, -0.5, -0.25,  0, 0.25, 0.5, 0.75, 1 ])
y = np.array([ None, None, None, None,  None, None, None, None, None ])

plt.plot(x, y, 'ro')
plt.xlim(-1, 1)
plt.ylim(-1, 1)

plt.xticks(x, ['', '', '', '', '0', 'x', r'x + $\Delta$x', '', ''])
plt.yticks(x, ['', '', '', '', '0', 'y', r'y + $\Delta$y', '', ''])

plt.axvline(x=0)
plt.axhline(y=0)

p = plt.axhspan(0.25, 0.5, facecolor='0.5', alpha=0.5)
p = plt.axvspan(0.25, 0.5, facecolor='0.5', alpha=0.5)

plt.title(r'Figure 1')
plt.grid(linestyle='dotted')

# plt.show()
plt.savefig('figure_1.png')
