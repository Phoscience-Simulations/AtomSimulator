from constants import *


def electrostatic(q1, q2, r):
    return CoulombConstant * (q1 * q2) / r**2