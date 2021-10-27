import matplotlib.pyplot as plt

import constants
import equation

xValues = [x/100 for x in range(80, 275)]
gap = 0.00001
yValues = [-(
               equation.strongForcePE(x * constants.Femtometre)-equation.strongForcePE((x-gap) * constants.Femtometre)
           ) / 1000000 * 1.6022e-13 / (gap * constants.Femtometre) for x in xValues]

plt.plot(xValues, yValues)
plt.axhline(y=0, color='r', linestyle='--')

plt.xlabel('Range (fm)')
plt.ylabel('Force (N)')

plt.title('Strong Force PE')

plt.show()
