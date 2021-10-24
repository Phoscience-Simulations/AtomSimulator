from math import floor
from time import time

import glm
import numpy as np
import pygame
from OpenGL.GL import *
from pygame import DOUBLEBUF, OPENGL
from pygame import GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES

import GameObjects
import ShaderLoader
import gamePaths
import numberShower
import quadHandler
from degreesMath import *
import constants


#  ffmpeg -i "No.1 - Kobasolo.mp3" "No.1 - Kobasolo2.wav"


def main():
    # Initialisation
    pygame.init()
    #pygame.mixer.init()
    GamePaths = gamePaths.PathHolder()

    display = 1366, 768
    displayV = glm.vec2(display)

    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    pygame.display.set_caption("Atom Simulator")

    iconSurface = pygame.image.load(GamePaths.iconPath)
    pygame.display.set_icon(iconSurface)

    pygame.display.flip()

    shader = ShaderLoader.compileShaders(*GamePaths.defaultShaderPaths)
    uiShader = ShaderLoader.compileShaders(*GamePaths.uiShaderPaths)
    glUseProgram(shader)

    uniformModel = glGetUniformLocation(shader, 'uniform_Model')
    uniformView = glGetUniformLocation(shader, 'uniform_View')
    uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')
    uniformLookAtMatrix = glGetUniformLocation(shader, 'lookAtMatrix')

    glUseProgram(shader)

    # ----- OpenGL Settings -----
    version = GL_VERSION
    print(f"OpenGL Version: {glGetString(version).decode()}")

    glMatrixMode(GL_PROJECTION)
    # gluPerspective(70, (displayV.X / displayV.Y), 0.1, 128.0)
    glViewport(0, 0, int(displayV.x), int(displayV.y))
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glClearColor(0, 0, 0, 1.0)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # ----- Camera Settings -----
    cameraRadius = 1
    cameraPos = glm.vec3(0, 0, cameraRadius)
    cameraFront = glm.vec3(0, 0, 0)
    cameraUp = glm.vec3(0, 1, 0)
    rotationXAngle = 0
    rotationYAngle = 90
    rotationZAngle = 0
    yDirection = 1

    cameraAccel = 0
    cameraVelocityDecay = 0.94
    cameraMinVelocity = 20
    cameraCurrentVelocity = 20

    # ----- Matrix Info -----
    projectionMatrix = glm.perspective(70, displayV.x / displayV.y, 1, 1000.0)
    modelMatrix = glm.mat4(1)

    glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                       glm.value_ptr(modelMatrix))

    glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                       glm.value_ptr(projectionMatrix))
    # ---- Particle Emitter ----
    particleEmitterObject = GameObjects.ParticleEmitter(shader, GamePaths.spherePath)

    # ----- UI -----
    fpsCounter = numberShower.NumberShower(uiShader,
                                           GamePaths.scoreBasePath,
                                           60 / displayV.y,
                                           glm.vec2(1-((3*10+2)/768), 1 - 62 / 768),
                                           displayV,
                                           maxDigitLength=3,
                                           defaultNumber="000")

    updateTime = quadHandler.TextQuad(uiShader, "Update Time: 0ms", GamePaths.mainFont, glm.vec2(displayV.x-5, 5)/displayV, 0.05, displayV, (255, 255, 255, 255), isTopRight=True)

    blurCount = 0

    screenQuad = GameObjects.ScreenQuad()

    times = [0]
    running = True
    clock = pygame.time.Clock()

    stopUpdate = False
    frameCount = 0

    while running:
        deltaT = clock.tick(60)
        s = time() * 1000

        frameCount += 1

        keyPressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not stopUpdate:
            cameraCurrentVelocity += cameraAccel
            cameraAccel = 0
            cameraCurrentVelocity *= cameraVelocityDecay
            cameraCurrentVelocity = max(cameraCurrentVelocity, cameraMinVelocity)

            rotationXAngle += deltaT / 1000 * cameraCurrentVelocity
            rotationYAngle += deltaT / 1000 * 45 * yDirection
            #rotationZAngle += deltaT / 1000 * 5

        if rotationYAngle > 360:
            rotationYAngle -= 360
        elif rotationYAngle < 0:
            rotationYAngle += 360
            
        if rotationXAngle > 360:
            rotationXAngle -= 360
        elif rotationXAngle < 0:
            rotationXAngle += 360

        if rotationZAngle > 360:
            rotationZAngle -= 360
        elif rotationZAngle < 0:
            rotationZAngle += 360

        """if rotationYAngle < 45:
            rotationYAngle = 45
            yDirection *= -1

        if rotationYAngle > 135:
            rotationYAngle = 135
            yDirection *= -1"""

        adjRotationY = sin(rotationYAngle)*45 + 90

        cameraHeight = sin(adjRotationY+90) * cameraRadius
        cameraAdjRadius = abs(cos(adjRotationY+90)) * cameraRadius

        cameraPos = glm.vec3(sin(rotationXAngle) * cameraAdjRadius, cameraHeight, cos(rotationXAngle) * cameraAdjRadius)
        #cameraUp = (sin(rotationZAngle), cos(rotationZAngle), 0)

        viewMatrix = glm.lookAt(cameraPos,
                                cameraFront,
                                cameraUp)

        particleLookMatrix = glm.mat4(1)

        yRotation = glm.rotate(particleLookMatrix, glm.radians(adjRotationY+90), (1, 0, 0))
        xRotation = glm.rotate(particleLookMatrix, glm.radians(rotationXAngle), (0, 1, 0))

        particleLookMatrix = xRotation * yRotation

        if not stopUpdate:
            # At 3000 particles, 23 ms to update
            particleEmitterObject.update(deltaT, pygame.time.get_ticks())

            #  At 3000 particles, 4ms to sort, 3ms to draw
            if frameCount % 2 == 0:
                particleEmitterObject.sort(cameraPos)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           glm.value_ptr(viewMatrix))

        glUniformMatrix4fv(uniformLookAtMatrix, 1, GL_FALSE,
                           glm.value_ptr(particleLookMatrix))

        particleEmitterObject.draw()

        glUseProgram(uiShader)
        fps = str(floor(clock.get_fps()))
        fpsCounter.setNumber(fps + "-"*(3-len(fps)))
        fpsCounter.draw()

        if frameCount % 10 == 0:
            tempTimes = times[-60:]
            updateTime.changeText(f"Frame Time: {floor(sum(tempTimes)/len(tempTimes))}ms")
        updateTime.draw()

        pygame.display.flip()

        e = time() * 1000
        ft = e - s
        times.append(ft)

    print("Average ms Per Frame", sum(times) / len(times))


if __name__ == "__main__":
    """import cProfile, pstats

    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()"""

    main()
