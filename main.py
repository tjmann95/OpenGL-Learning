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

    vertices = [
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0
    ]

    vertices = np.array(vertices, dtype=np.float32)

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

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    shader = Shader("vertex.vs", "fragment.fs").compile_shader()
    glUseProgram(shader)

    while not glfw.window_should_close(window):
        process_input(window)

        glClearColor(.2, .3, .3, 1.)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader)
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
