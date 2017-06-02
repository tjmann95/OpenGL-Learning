#version 330
in vec2 texCoordOut;
in vec3 Normal;
in vec3 FragPos;
in vec3 LightPos;

out vec4 outColor;

struct Material {
    float shininess;
};

struct Light {
    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

uniform sampler2D diffuse;
uniform sampler2D specular;
uniform sampler2D emission;
uniform vec3 objectColor;
uniform vec3 lightColor;
uniform Material material;
uniform Light light;

void main()
{
    //ambient
    vec3 ambient = light.ambient * vec3(texture(diffuse, texCoordOut));

    //diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(LightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * vec3(texture(diffuse, texCoordOut));

    //specular
    vec3 viewDir = normalize(-FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * spec * vec3(texture(specular, texCoordOut));

    //emision
    vec3 emissionColor = texture(emission, texCoordOut).rgb;

    //outColor = texture(samplerTexture, texCoordOut);
    vec3 result = ambient + diffuse + specular;
    outColor = vec4(result, 1.0);
}