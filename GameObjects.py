from random import random, randint

import glm

import OBJParser
import VBOHandler
import constants
import equation
from degreesMath import *


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
        self.particleCount = 50

        self.particleSpawnRadius = constants.Femtometre*2

        self.sphereObj = OBJParser.OBJObject(spherePath)

        # Electron Neutron Proton
        colours = [[1, 1, 0, 1], [0, 0, 1, 1], [1, 0, 0, 1]]
        charge = [-1, 0, 1]
        masses = [constants.NeutronMass/1836, constants.NeutronMass, constants.ProtonMass]
        scale = [constants.Femtometre*0.1, constants.Femtometre*0.8, constants.Femtometre*0.877]

        self.particles = []
        for i in range(self.particleCount):
            newPos = self.generateSpawnPos()
            particleType = randint(-1, 1)
            particleIndex = particleType + 1

            self.particles.append({
                "position": newPos,
                "scale": scale[particleIndex],
                "color": colours[particleIndex],
                "charge": charge[particleIndex] * constants.ElementaryCharge,
                "velocity": glm.vec3(),
                "acceleration": glm.vec3(),
                "mass": masses[particleIndex],
                "force": glm.vec3(),
                "rotation": random() * 360,
                "lifetime": 500,
                "draw": 1,
                "timestamp": 0  # Creation Date
            })

        self.VBO = VBOHandler.VBOParticle(shader, self.sphereObj.vertices, self.sphereObj.faces, self.sphereObj.faceNormals, self.particles)

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

    #@line_profiler_pycharm.profile
    def update(self, deltaT, currentTime):
        deltaTS = deltaT / 1000
        self.updateCount += 1

        for particle in self.particles:
            particle["acceleration"] = glm.vec3(0, 0, 0)
            particle["force"] = glm.vec3(0, 0, 0)

        for ia, particleA in enumerate(self.particles):
            for ib, particleB in enumerate(self.particles):
                if particleA is not particleB and particleA["draw"] and particleB["draw"]:
                    relativeV = particleB["position"] - particleA["position"]
                    length = glm.length(relativeV)
                    relativeVN = glm.normalize(relativeV)

                    esForce = equation.electrostatic(
                        particleA["charge"],
                        particleB["charge"],
                        length
                    )
                    forceESVector = relativeVN * -esForce
                    particleA["force"] += forceESVector

                    if particleA["charge"] >= 0 and particleB["charge"] >= 0:
                        sfForce = equation.strongForce(length)
                        forceSFVector = relativeVN * -sfForce
                        particleA["force"] += forceSFVector

        for i, particle in enumerate(self.particles):
            particle["acceleration"] = particle["force"] / particle["mass"]
            particle["velocity"] += particle["acceleration"] * deltaTS
            particle["position"] += particle["velocity"] * deltaTS

            #print(i, "Position", particle["position"])
            #print(i, "V", particle["velocity"], "F", particle["force"], "A", particle["acceleration"], "DTS", deltaTS)

        self.VBO.update()

    def draw(self):
        self.VBO.draw()
