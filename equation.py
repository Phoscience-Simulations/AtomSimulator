rom constants import *
#import numba
from numpy import exp
# import numba
from numpy import exp

from constants import *


#@numba.jit()
def electrostatic(q1, q2, r):
    return CoulombConstant * (q1 * q2) / r**2


def strongForcePE(r):
    nuR = nu * r / Femtometre
    return ((-10.463 * exp(-nuR)/nuR) - (1650.6 * exp(-4*nuR)/nuR) + (6482.2 * exp(-7*nuR)/nuR)) * 1_000_000


deltaD = 0.00001 * Femtometre
def strongForce(r):
    return -(strongForcePE(r)-strongForcePE(r-deltaD)) / 1000000 * MegaElectronVoltsToJoules / deltaD
#  0.8446691956fm ~ 0N
