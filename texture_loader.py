from PIL import Image
from OpenGL.GL import *

def load_texture(path, flip):
    tex_id = glGenTextures(1)

    image = Image.open(path)
    if flip:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    data = image.convert("RGBA").tobytes()

    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return tex_id


class Texture:

    def __init__(self, texturepath, flip):
        self.path = texturepath
        self.flip = flip

        self.tex_ID = load_texture(self.path, self.flip)
