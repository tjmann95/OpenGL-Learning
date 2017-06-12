#version 330
layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoord;
layout (location = 2) in vec3 normal;
layout (location = 3) in vec3 grassPosition;
layout (location = 4) in vec3 grassTexCoord;

out vec2 texCoordOut;
out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    FragPos = vec3(model * vec4(position, 1.0));
    texCoordOut = texCoord;
    Normal = mat3(transpose(inverse(model))) * normal;
}
