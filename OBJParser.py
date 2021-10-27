import glm


class OBJObject:
    def __init__(self, objPath):
        self.vertices = []
        self.faces = []
        self.faceNormals = []

        self.normals = []

        with open(objPath, 'r') as objFile:
            data = objFile.readlines()

            #  Assuming that the string side startswith is in order in the obj file
            for line in data:
                lineData = line.split(" ")[1:]

                if line.startswith('vn'):
                    lineDataI = [float(x) for x in lineData]
                    self.normals.append(glm.vec3(lineDataI))
                elif line.startswith('v'):
                    lineDataI = [float(x) for x in lineData]
                    self.vertices.append(glm.vec3(lineDataI))
                elif line.startswith('f'):
                    lineDataI = [[int(y) for y in x.split("//")] for x in lineData]
                    lineDataF = [x[0] for x in lineDataI]
                    lineDataN = [x[1] for x in lineDataI]

                    self.faces.append(glm.vec3(lineDataF))
                    self.faceNormals.append(glm.vec3(lineDataN))
