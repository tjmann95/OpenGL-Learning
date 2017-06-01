#version 330
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vertColor;
layout (location = 2) in vec2 texCoord;

out vec3 vertexColor;
out vec2 texCoordOut;

void main()
{
    gl_Position = vec4(position, 1.0);
    vertexColor = vertColor;
    texCoordOut = texCoord;
}
