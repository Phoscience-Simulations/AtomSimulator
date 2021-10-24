import sys
from os import path


class PathHolder:
    def __init__(self):
        self.resources = path.abspath(path.join(".", "resources"))

        self.iconPath = path.join(self.resources, "icon.png")
        self.spherePath = path.join(self.resources, "sphere.obj")

        self.imagesPath = path.join(self.resources, "images")
        self.scorePath = path.join(self.imagesPath, "score")
        self.scoreBasePath = path.join(self.scorePath, "score@2x.png")

        self.shaderPath = path.join(".", "shaders")

        self.vertexPath = path.join(self.shaderPath, "vertex.shader")
        self.fragmentPath = path.join(self.shaderPath, "fragment.shader")
        self.defaultShaderPaths = (self.vertexPath, self.fragmentPath)

        self.uiVertexPath = path.join(self.shaderPath, "UIvertex.shader")
        self.uiFragmentPath = path.join(self.shaderPath, "UIfragment.shader")
        self.uiShaderPaths = (self.uiVertexPath, self.uiFragmentPath)

        self.fontsPath = path.join(self.resources, "fonts")

        self.allerPath = path.join(self.fontsPath, "Aller")
        self.mainFont = path.join(self.allerPath, "Aller_Lt.ttf")
        self.mainFont2 = path.join(self.allerPath, "Aller_Rg.ttf")


