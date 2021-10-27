from random import random
from time import time

import glm

iteration = 100**2

init = glm.vec3(random(), random(), random())

def glmLength(vector):
    return glm.length(vector)

dataset = [glm.vec3(random(), random(), random()) for i in range(iteration)]
s = time()

for data in dataset:
    glmLength(data - init)

e = time() - s
print(f"glm.length: {e} seconds, {e/iteration}s per iteration")