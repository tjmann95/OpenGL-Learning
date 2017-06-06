#version 330

#define NR_POINT_LIGHTS 4

in vec2 texCoordOut;
in vec3 Normal;
in vec3 FragPos;

out vec4 outColor;

uniform sampler2D diffuse;
uniform sampler2D specular;
uniform sampler2D emission;

uniform vec3 viewPos;

struct Material {
    float shininess;
};

uniform Material material;

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);

    //diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    //specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);

    //net
    vec3 ambient = light.ambient * vec3(texture(diffuse, texCoordOut));
    vec3 diffuse = light.diffuse * diff * vec3(texture(diffuse, texCoordOut));
    vec3 specular = light.specular * spec * vec3(texture(specular, texCoordOut));
    return (ambient + diffuse + specular);
}

uniform DirLight dirLight;

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);

    //diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    //specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);

    //attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    //net
    vec3 ambient  = light.ambient  * vec3(texture(diffuse, texCoordOut));
    vec3 diffuse  = light.diffuse  * diff * vec3(texture(diffuse, texCoordOut));
    vec3 specular = light.specular * spec * vec3(texture(specular, texCoordOut));
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}

uniform PointLight pointLights[NR_POINT_LIGHTS];

void main()
{
    //properties
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    //Directional
    vec3 result = CalcDirLight(dirLight, norm, viewDir);

    //Point
    for(int i = 0; i < NR_POINT_LIGHTS; i++)
        result += CalcPointLight(pointLights[i], norm, FragPos, viewDir);

    outColor = vec4(result, 1.0);
}