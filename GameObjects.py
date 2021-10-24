import colorsys
from dataclasses import dataclass
from math import floor
from random import random
from time import time

import glm

import VBOHandler
import constants
from degreesMath import *
#import line_profiler_pycharm
import pywavefront
import constants


class ScreenQuad:
    def __init__(self):
        self.vertices = [
            glm.vec3(-1, 1, 0),
            glm.vec3(-1, -1, 0),
            glm.vec3(1, 1, 0),
            glm.vec3(1, -1, 0)
        ]

        self.textureCoords = [
            glm.vec2(0, 1),
            glm.vec2(0, 0),
            glm.vec2(1, 1),
            glm.vec2(1, 0),
        ]

        self.quadVBO = VBOHandler.VBOScreen(self.vertices, self.textureCoords)

    def draw(self):
        self.quadVBO.draw()


class ParticleEmitter:
    def __init__(self, shader, spherePath):
        self.particleCount = 3

        self.particleSpawnRadius = constants.Femtometre * 3

        self.circleVertices = []
        self.circleFaces = []

        self.sphereObj = pywavefront.Wavefront(spherePath, collect_faces=True)
        self.maxVertex = glm.vec3(0, 0, 0)
        self.minVertex = glm.vec3(0, 0, 0)

        for vertex in self.sphereObj.vertices:
            self.circleVertices.append(glm.vec3(vertex))

        for face in self.sphereObj.meshes["Sphere"].faces:
            self.circleFaces.append(glm.vec3(face))

        self.particles = []
        for i in range(self.particleCount):
            newPos = self.generateSpawnPos()

            self.particles.append({
                "position": newPos,
                "scale": 0.1,
                "color": [*colorsys.hsv_to_rgb(random(), 1, 1), 1],
                "rotation": random() * 360,
                "lifetime": 500,
                "draw": 1,
                "timestamp": 0  # Creation Date
            })

        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.circleFaces, self.particles)

        self.updateCount = 0

    def generateSpawnPos(self):
        u1 = random()
        u2 = random()

        latitude = acos(2 * u1 - 1) - 90  # -90 -> 90 ==>
        #latitude = (acos(2 * u1 - 1) - 90)*0.1 + 180  # -90 -> 90 ==>
        #latitude = 45

        longitude = 2 * 180 * u2

        return glm.vec3(
            cos(latitude) * cos(longitude),
            cos(latitude) * sin(longitude),
            sin(latitude),
        ) * self.particleSpawnRadius

    def sort(self, cameraPos):
        def particleSortFunction(particle):
            return glm.length(particle["position"] - cameraPos)

        self.particles = sorted(self.particles, key=particleSortFunction,
                                reverse=True)
        self.VBO.particles = self.particles

    def update(self, deltaT, currentTime):
        self.updateCount += 1

        for particleA in self.particles:
            for particleB in self.particles:
                if particleA is not particleB and particleA["draw"] and particleB["draw"]:
                    pass


        self.VBO.update()

    def draw(self):
        self.VBO.draw()
