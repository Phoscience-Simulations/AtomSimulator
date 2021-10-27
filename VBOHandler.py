import ctypes

import numpy as np
from OpenGL.GL import glGenBuffers, glGetAttribLocation, glBindBuffer, glBufferData, glDrawElementsInstanced, \
    glBindVertexArray, glGenVertexArrays, glVertexAttribPointer, glDrawArrays, glBufferSubData, \
    glEnableVertexAttribArray, glBindTexture, glDrawElements, glEnable, \
    glVertexAttribDivisor, GL_STATIC_DRAW, GL_TRIANGLE_STRIP, GL_DYNAMIC_DRAW, GL_UNSIGNED_INT, GL_ELEMENT_ARRAY_BUFFER, \
    GL_ARRAY_BUFFER, \
    GL_FLOAT, GL_FALSE, \
    GL_TRIANGLES, GL_TEXTURE_2D


class VBOScreen:
    def __init__(self, vertices, textureCoords):
        self.vertices = vertices
        self.textureCoords = textureCoords

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object

        self.polygon = []

        for i in range(len(self.vertices)):
            self.polygon.extend(self.vertices[i].to_list() + self.textureCoords[i].to_list())

        self.polygon = np.array(self.polygon, dtype=np.float32)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.polygon), self.polygon, GL_STATIC_DRAW)

        self.stride = (3+2) * 4

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.stride, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.vertices))
        glBindVertexArray(0)


class VBOParticle:
    def __init__(self, shader, vertices, faces, normals, particles):
        self.vertices = vertices
        self.normals = normals
        self.particles = particles
        self.particleData = self.serializeParticles()

        self.polygon = self.generatePolygon()
        self.normalVectors = self.generateNormals()

        indices = []
        for face in faces:
            indices.extend(face.to_list())

        self.indices = np.array(indices, dtype=np.uint32)

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object
        self.PBO = glGenBuffers(1)  # Position Buffer Object
        self.EBO = glGenBuffers(1)  # Element Buffer Object
        self.NBO = glGenBuffers(1)  # Normal Buffer Object

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.polygon), self.polygon, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.particleData), self.particleData, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.NBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.normalVectors), self.normalVectors, GL_STATIC_DRAW)

        self.vertexStride = 3 * 4
        self.particleStride = (3 + 4 + 1 + 1) * 4

        self.vertexPositionLocation = glGetAttribLocation(shader, "vertexPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glVertexAttribPointer(self.vertexPositionLocation, 3, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.vertexPositionLocation)

        self.normalVectorLocation = glGetAttribLocation(shader, "normalVector")
        glBindBuffer(GL_ARRAY_BUFFER, self.NBO)
        glVertexAttribPointer(self.normalVectorLocation, 3, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.normalVectorLocation)

        self.worldPositionLocation = glGetAttribLocation(shader, "worldPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glVertexAttribPointer(self.worldPositionLocation, 3, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p(0))
        glVertexAttribDivisor(self.worldPositionLocation, 1)
        glEnableVertexAttribArray(self.worldPositionLocation)

        self.colorLocation = glGetAttribLocation(shader, "color")
        glVertexAttribPointer(self.colorLocation, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p(3 * 4))
        glVertexAttribDivisor(self.colorLocation, 1)
        glEnableVertexAttribArray(self.colorLocation)

        self.scaleLocation = glGetAttribLocation(shader, "scale")
        glVertexAttribPointer(self.scaleLocation, 1, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4) * 4))
        glVertexAttribDivisor(self.scaleLocation, 1)
        glEnableVertexAttribArray(self.scaleLocation)

        self.drawLocation = glGetAttribLocation(shader, "draw")
        glVertexAttribPointer(self.drawLocation, 1, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4+1) * 4))
        glVertexAttribDivisor(self.drawLocation, 1)
        glEnableVertexAttribArray(self.drawLocation)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update(self):
        glBindVertexArray(self.VAO)

        self.particleData = self.serializeParticles()

        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glBufferSubData(GL_ARRAY_BUFFER, 0, len(self.particleData) * 4, self.particleData)

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawElementsInstanced(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None, len(self.particles))
        glBindVertexArray(0)

    def serializeParticles(self):
        particleData = []
        for particle in self.particles:
            particleData.extend(particle["position"].to_list() + particle["color"] + [particle["scale"], particle["draw"]])

        return np.array(particleData, dtype=np.float32)

    def generateNormals(self):
        normalVectors = []
        for normal in self.normals:
            normalVectors.extend(normal.to_list())

        return np.array(normalVectors, dtype=np.float32)

    def generatePolygon(self):
        polygon = []
        for vertex in self.vertices:
            polygon.extend(vertex.to_list())

        return np.array(polygon, dtype=np.float32)


class VBOImage:
    def __init__(self, shader, vertices, colours, textureCoords, texture):
        self.vertices = vertices
        self.colours = colours
        self.textureCoords = textureCoords

        self.texture = texture

        self.vertexData = self.serializeData()

        indices = []
        for i in range(len(vertices) - 2):
            indices.extend([
                0,
                i + 1,
                i + 2
            ])

        self.indices = np.array(indices, dtype=np.uint32)

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object
        self.EBO = glGenBuffers(1)  # Element Buffer Object

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.vertexData), self.vertexData, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        self.vertexStride = (2 + 4 + 2) * 4

        self.positionLocation = glGetAttribLocation(shader, "position")
        glVertexAttribPointer(self.positionLocation, 2, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.positionLocation)

        self.colourLocation = glGetAttribLocation(shader, "colour")
        glVertexAttribPointer(self.colourLocation, 4, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(8))
        glEnableVertexAttribArray(self.colourLocation)

        self.texCoordsLocation = glGetAttribLocation(shader, "textureCoords")
        glVertexAttribPointer(self.texCoordsLocation, 2, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(self.texCoordsLocation)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update(self):
        glBindVertexArray(self.VAO)

        self.vertexData = self.serializeData()

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferSubData(GL_ARRAY_BUFFER, 0, len(self.vertexData) * 4, self.vertexData)

        glBindVertexArray(0)

    def serializeData(self):
        combinedData = []

        for i in range(len(self.vertices)):
            combinedData.extend(self.vertices[i].to_list())
            combinedData.extend(self.colours[i])
            combinedData.extend(self.textureCoords[i])

        return np.array(combinedData, dtype=np.float32)

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
