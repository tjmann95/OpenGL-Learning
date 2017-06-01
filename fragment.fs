#version 330
in vec3 vertexColor;
in vec2 texCoordOut;

out vec4 color;

uniform sampler2D ourTexture1;
uniform sampler2D ourTexture2;

void main()
{
    color = mix(texture(ourTexture1, texCoordOut), texture(ourTexture2, texCoordOut), .2);
}
