#version 330
in vec2 texCoordOut;

out vec4 color;

uniform sampler2D ourTexture;

void main()
{
    color = texture(ourTexture, texCoordOut);
}
