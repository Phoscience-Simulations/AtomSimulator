#version 450 core

uniform vec3 cameraPos;
uniform vec3 lightPos;
uniform float ambient;

in PARTICLEOUT {
    int valid;
} particlein;

in vec4 fragColor;
in vec3 fragPosition;
in vec3 fragNormal;

layout (location = 0) out vec4 outColor;

float specularStrength = 0.5;

void main()
{
    if (particlein.valid == 0){
        discard;
    }

    vec3 norm = fragNormal;
    vec3 lightDir = normalize(lightPos - fragPosition);

    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1, 1, 1); // Light Colour

    vec3 result = (ambient + diffuse) * fragColor.xyz;
    outColor = vec4(result, 1);
}