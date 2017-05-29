#version 330
in vec3 ourColor;
in vec2 texCoordsOut;

out vec4 color;

uniform sampler2D woodTexture;
uniform sampler2D faceTexture;

uniform vec3 objectColor;
uniform vec3 lightColor;

void main()
{
    //color = mix(texture(woodTexture, texCoordsOut), texture(faceTexture, texCoordsOut), 0.2);
    color = vec4(lightColor * objectColor, 1.0);
}