import glfw
import numpy as np

from OpenGL.GL import *
from shader_loader import Shader
from PIL import Image


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def process_input(window):
    global mixValue

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def main():

    vertices = [
       # Vertices        Colors             Texture Coordinates
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,    0.0, 0.0,
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,    1.0, 0.0,
         0.5,  0.5, 0.0,  0.0, 0.0, 1.0,    1.0, 1.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 0.0,    0.0, 1.0
    ]

    indices = [
        0, 1, 2,
        0, 2, 3
    ]

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    glfw.init()

    window_width = 800
    window_height = 600
    window = glfw.create_window(window_width, window_height, "Learning", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glViewport(0, 0, window_width, window_height)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs")

    vao = GLuint(0)
    vbo = GLuint(0)

    glGenVertexArrays(1, vao)
    glGenBuffers(1, vbo)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(0 * vertices.itemsize))
    glEnableVertexAttribArray(0)

    # Color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # Texture
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Loading texture
    texture_image1 = Image.open("resources\\cobblestone.png")
    texture_image1 = texture_image1.transpose(Image.FLIP_TOP_BOTTOM)
    texture_data1 = texture_image1.convert("RGBA").tobytes()

    texture_image2 = Image.open("resources\\awesomeface.png")
    texture_image2 = texture_image2.transpose(Image.FLIP_TOP_BOTTOM)
    texture_data2 = texture_image2.convert("RGBA").tobytes()

    # Generating texture
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_image1.width, texture_image1.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data1)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Texture 2
    texture2 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture2)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_image2.width, texture_image2.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data2)
    glGenerateMipmap(GL_TEXTURE_2D)

    while not glfw.window_should_close(window):
        process_input(window)

        glClearColor(.2, .3, .3, 1.)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader.shader_program)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture1)
        glUniform1i(glGetUniformLocation(shader.shader_program, "ourTexture1"), 0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture2)
        glUniform1i(glGetUniformLocation(shader.shader_program, "ourTexture2"), 1)

        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        # glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
