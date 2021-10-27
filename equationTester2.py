import matplotlib.pyplot as plt

import constants
import equation

xValues = [x/100 for x in range(50, 300)]
yValues = [equation.electrostatic(constants.ElementaryCharge,
                                  constants.ElementaryCharge,
                                  x * constants.Femtometre) for x in xValues]

plt.plot(xValues, yValues)

plt.xlabel('Range (fm)')
plt.ylabel('Force (N)')

plt.title('Electrostatic Force')

plt.show()
