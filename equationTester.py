import matplotlib.pyplot as plt

import constants
import equation

xValues = [x/100 for x in range(60, 300)]
yValues = [equation.strongForcePE(x * constants.Femtometre) / 1000000 for x in xValues]

plt.plot(xValues, yValues)

plt.xlabel('Range (fm)')
plt.ylabel('Potential Energy (MeV)')

plt.title('Strong Force PE')

plt.show()
