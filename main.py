import glfw
import numpy as np

from OpenGL.GL import *
from shader_loader import Shader


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def main():

    vertices1 = [
        -0.9, -0.5, 0.0,
         0.0, -0.5, 0.0,
        -0.45, 0.5, 0.0,
        #-0.5,  0.5, 0.0
    ]

    vertices2 = [
         0.0, -0.5, 0.0,
         0.9, -0.5, 0.0,
         0.45, 0.5, 0.0,
        #-0.5,  0.5, 0.0
    ]

    indices = [
        0, 1, 2,
        0, 2, 3
    ]

    vertices1 = np.array(vertices1, dtype=np.float32)
    vertices2 = np.array(vertices2, dtype=np.float32)
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

    shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs").compile_shader()

    vao = [GLuint()] * 2
    vbo = [GLuint()] * 2
    glGenVertexArrays(1, vao[0])
    glGenBuffers(1, vbo[0])
    glGenVertexArrays(1, vao[1])
    glGenBuffers(1, vbo[1])

    glBindVertexArray(vao[0])
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vertices1.nbytes, vertices1, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0 * vertices1.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindVertexArray(vao[1])
    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, vertices2.nbytes, vertices2, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0 * vertices2.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # ebo = glGenBuffers(1)
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    # glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    while not glfw.window_should_close(window):
        process_input(window)

        glClearColor(.2, .3, .3, 1.)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader)
        glBindVertexArray(vao[0])
        # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glBindVertexArray(vao[1])
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
