#version 450 core
uniform mat4 uniform_Model;
uniform mat4 uniform_View;
uniform mat4 uniform_Projection;
uniform mat4 lookAtMatrix;

in vec3 vertexPosition;
in vec3 worldPosition;
in vec3 normalVector;
in vec4 color;
in float scale;
in int draw;

out PARTICLEOUT {
    int valid;
} particleout;

out vec4 fragColor;
out vec3 fragPosition;
out vec3 fragNormal;

void main()
{
    vec4 rawPosition = uniform_Model * (vec4(worldPosition, 1) + (vec4(vertexPosition * scale,1)));
    gl_Position = uniform_Projection * uniform_View * rawPosition;

    particleout.valid = draw;

    fragColor = color;
    fragPosition = rawPosition.xyz;
    fragNormal = normalVector;
}