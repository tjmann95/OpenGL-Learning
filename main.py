import glfw
import numpy as np

from OpenGL.GL import *
from shader_loader import Shader
from PIL import Image
from pyrr import Quaternion, Matrix44, Vector3, vector, vector3
from math import radians
from camera import Camera
from math import sin, cos

cam = Camera()
cam_speed = .01
last_x, last_y = 400, 400
first_mouse = True
keys = [False] * 1024

light_pos = Vector3([1.2, 1.0, 2.0])

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def key_callback(window, key, scancode, action, mode):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key >= 0 and key < 1024:
        if action == glfw.PRESS:
            keys[key] = True
        if action == glfw.RELEASE:
            keys[key] = False


def move():
    if keys[glfw.KEY_W]:
        cam.process_keyboard("FORWARD", cam_speed)
    if keys[glfw.KEY_S]:
        cam.process_keyboard("BACKWARD", cam_speed)
    if keys[glfw.KEY_A]:
        cam.process_keyboard("LEFT", cam_speed)
    if keys[glfw.KEY_D]:
        cam.process_keyboard("RIGHT", cam_speed)
    if keys[glfw.KEY_SPACE]:
        cam.process_keyboard("UP", cam_speed)
    if keys[glfw.KEY_LEFT_SHIFT]:
        cam.process_keyboard("DOWN", cam_speed)


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y
    sensitivity = 1.2

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False

    x_offset = xpos - last_x
    y_offset = last_y - ypos
    last_x = xpos
    last_y = ypos
    x_offset *= sensitivity
    y_offset *= sensitivity

    cam.process_mouse_movement(x_offset, y_offset)


def main():

    vertices = [
       # Vertices           Texture     Normals
        -0.5, -0.5, -0.5,   0.0, 0.0,   0.0, 0.0, -1.0,
         0.5, -0.5, -0.5,   1.0, 0.0,   0.0, 0.0, -1.0,
         0.5,  0.5, -0.5,   1.0, 1.0,   0.0, 0.0, -1.0,
         0.5,  0.5, -0.5,   1.0, 1.0,   0.0, 0.0, -1.0,
        -0.5,  0.5, -0.5,   0.0, 1.0,   0.0, 0.0, -1.0,
        -0.5, -0.5, -0.5,   0.0, 0.0,   0.0, 0.0, -1.0,

        -0.5, -0.5,  0.5,   0.0, 0.0,   0.0, 0.0,  1.0,
         0.5, -0.5,  0.5,   1.0, 0.0,   0.0, 0.0,  1.0,
         0.5,  0.5,  0.5,   1.0, 1.0,   0.0, 0.0,  1.0,
         0.5,  0.5,  0.5,   1.0, 1.0,   0.0, 0.0,  1.0,
        -0.5,  0.5,  0.5,   0.0, 1.0,   0.0, 0.0,  1.0,
        -0.5, -0.5,  0.5,   0.0, 0.0,   0.0, 0.0,  1.0,

        -0.5,  0.5,  0.5,   1.0, 0.0,  -1.0, 0.0,  0.0,
        -0.5,  0.5, -0.5,   1.0, 1.0,  -1.0, 0.0,  0.0,
        -0.5, -0.5, -0.5,   0.0, 1.0,  -1.0, 0.0,  0.0,
        -0.5, -0.5, -0.5,   0.0, 1.0,  -1.0, 0.0,  0.0,
        -0.5, -0.5,  0.5,   0.0, 0.0,  -1.0, 0.0,  0.0,
        -0.5,  0.5,  0.5,   1.0, 0.0,  -1.0, 0.0,  0.0,

         0.5,  0.5,  0.5,   1.0, 0.0,   1.0, 0.0,  0.0,
         0.5,  0.5, -0.5,   1.0, 1.0,   1.0, 0.0,  0.0,
         0.5, -0.5, -0.5,   0.0, 1.0,   1.0, 0.0,  0.0,
         0.5, -0.5, -0.5,   0.0, 1.0,   1.0, 0.0,  0.0,
         0.5, -0.5,  0.5,   0.0, 0.0,   1.0, 0.0,  0.0,
         0.5,  0.5,  0.5,   1.0, 0.0,   1.0, 0.0,  0.0,

        -0.5, -0.5, -0.5,   0.0, 1.0,   0.0,-1.0,  0.0,
         0.5, -0.5, -0.5,   1.0, 1.0,   0.0,-1.0,  0.0,
         0.5, -0.5,  0.5,   1.0, 0.0,   0.0,-1.0,  0.0,
         0.5, -0.5,  0.5,   1.0, 0.0,   0.0,-1.0,  0.0,
        -0.5, -0.5,  0.5,   0.0, 0.0,   0.0,-1.0,  0.0,
        -0.5, -0.5, -0.5,   0.0, 1.0,   0.0,-1.0,  0.0,

        -0.5,  0.5, -0.5,   0.0, 1.0,   0.0, 1.0,  0.0,
         0.5,  0.5, -0.5,   1.0, 1.0,   0.0, 1.0,  0.0,
         0.5,  0.5,  0.5,   1.0, 0.0,   0.0, 1.0,  0.0,
         0.5,  0.5,  0.5,   1.0, 0.0,   0.0, 1.0,  0.0,
        -0.5,  0.5,  0.5,   0.0, 0.0,   0.0, 1.0,  0.0,
        -0.5,  0.5, -0.5,   0.0, 1.0,   0.0, 1.0,  0.0
    ]

    indices = [
        0, 1, 2,
        0, 2, 3
    ]

    block_positions = [
        Vector3([0, 0, 0]),
        Vector3([1, 0, 0]),
        Vector3([-1, 0, 0]),
        Vector3([0, 0, 1]),
        Vector3([1, 0, 1]),
        Vector3([-1, 0, 1]),
        Vector3([0, 0, -1]),
        Vector3([1, 0, -1]),
        Vector3([-1, 0, -1]),
    ]

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    glfw.init()

    window_width = 800
    window_height = 800
    aspect_ratio = window_width / window_height
    window = glfw.create_window(window_width, window_height, "Learning", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    glViewport(0, 0, window_width, window_height)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)

    glEnable(GL_DEPTH_TEST)

    shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs")
    lighting_shader = Shader("shaders\\lighting_vertex.vs", "shaders\\lighting_fragment.fs")

    vao = []
    vbo = []

    vao.append(GLuint())
    vbo.append(GLuint())

    # Cube 1
    glGenVertexArrays(1, vao[0])
    glGenBuffers(1, vbo[0])

    glBindVertexArray(vao[0])
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(0 * vertices.itemsize))
    glEnableVertexAttribArray(0)

    # Texture
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # Normal
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(5 * vertices.itemsize))
    glEnableVertexAttribArray(2)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Cube 2
    vao.append(GLuint())
    glGenVertexArrays(1, vao[1])
    glBindVertexArray(vao[1])
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])

    # Cube 2 attributes
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize, ctypes.c_void_p(0 * vertices.itemsize))
    glEnableVertexAttribArray(0)

    # Loading texture
    texture_image = Image.open("resources\\container.png")
    texture_image = texture_image.transpose(Image.FLIP_TOP_BOTTOM)
    texture_data = texture_image.convert("RGBA").tobytes()

    spec_texture_image = Image.open("resources\\container_specular.png")
    spec_texture_image = spec_texture_image.transpose(Image.FLIP_TOP_BOTTOM)
    spec_texture_data = spec_texture_image.convert("RGBA").tobytes()

    emission_texture_image = Image.open("resources\\matrix.png")
    emission_texture_image = emission_texture_image.transpose(Image.FLIP_TOP_BOTTOM)
    emission_texture_data = emission_texture_image.convert("RGBA").tobytes()

    # Generating texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_image.width, texture_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    spec_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, spec_texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, spec_texture_image.width, spec_texture_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, spec_texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    emission_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, emission_texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, emission_texture_image.width, emission_texture_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, emission_texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    last_frame = 0.0

    while not glfw.window_should_close(window):
        glfw.poll_events()
        move()

        glClearColor(.2, .3, .3, 1.)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        time = glfw.get_time()
        delta_time = time - last_frame
        last_frame = time

        glUseProgram(shader.shader_program)

        # Texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, spec_texture)

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, emission_texture)

        # Send material to shader
        glUniform1f(glGetUniformLocation(shader.shader_program, "material.shininess"), 32.0)

        # Send light to shader
        glUniform3f(glGetUniformLocation(shader.shader_program, "lightPos"), light_pos.x, light_pos.y, light_pos.z)
        glUniform3f(glGetUniformLocation(shader.shader_program, "light.ambient"), .2, .2, .2)
        glUniform3f(glGetUniformLocation(shader.shader_program, "light.diffuse"), .5, .5, .5)
        glUniform3f(glGetUniformLocation(shader.shader_program, "light.specular"), 1.0, 1.0, 1.0)

        # Send view position to shader
        glUniform3f(glGetUniformLocation(shader.shader_program, "viewPos"), cam.camera_pos[0], cam.camera_pos[1], cam.camera_pos[2])

        # Send light map to shader
        glUniform1i(glGetUniformLocation(shader.shader_program, "diffuse"), 0)
        glUniform1i(glGetUniformLocation(shader.shader_program, "specular"), 1)

        # Get transformation locations
        model_loc = glGetUniformLocation(shader.shader_program, "model")
        view_loc = glGetUniformLocation(shader.shader_program, "view")
        projection_loc = glGetUniformLocation(shader.shader_program, "projection")

        # Get uniform locations
        object_color_loc = glGetUniformLocation(shader.shader_program, "objectColor")
        light_color_loc = glGetUniformLocation(shader.shader_program, "lightColor")

        glUniform3f(object_color_loc, 1.0, 0.5, 0.31)
        glUniform3f(light_color_loc, 1.0, 1.0, 1.0)

        view_matrix = cam.get_view_matrix()
        view_matrix = np.array(view_matrix, dtype=np.float32)

        # Create projection matrix
        projection_matrix = Matrix44.perspective_projection(45.0, aspect_ratio, 0.1, 100.0)
        projection_matrix = np.array(projection_matrix, dtype=np.float32)

        # Send view projection transformations to shader
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection_matrix)

        for each_block in range(0, len(block_positions)):
            # Create model matrix
            model_matrix = Matrix44.identity()  # Scale model by 1

            model_rotation_x = Quaternion.from_x_rotation(0)  # Rotate about x
            model_orientation_x = model_rotation_x * Quaternion()  # Create orientation matrix x
            model_rotation_y = Quaternion.from_y_rotation(0)  # Rotate about y
            model_orientation_y = model_rotation_y * Quaternion()  # Create orientation matrix y
            model_rotation_z = Quaternion.from_z_rotation(0)  # Rotate about z
            model_orientation_z = model_rotation_z * Quaternion()  # Create orientation matrix z

            model_translation = block_positions[each_block]
            model_translation = Matrix44.from_translation(model_translation)

            model_matrix = model_matrix * model_orientation_x  # Apply orientation x
            model_matrix = model_matrix * model_orientation_y  # Apply orientation y
            model_matrix = model_matrix * model_orientation_z  # Apply orientation z
            model_matrix = model_matrix * model_translation  # Apply translation
            model_matrix = np.array(model_matrix, dtype=np.float32)  # Convert to opengl data type

            # Send model transform to shader
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix)

            # Draw cube 1
            glBindVertexArray(vao[0])

            glDrawArrays(GL_TRIANGLES, 0, 36)

        # -------------------------------------------------------------------------------------
        # Draw light
        # glUseProgram(lighting_shader.shader_program)
        #
        # # Get transformation locations
        # model_loc = glGetUniformLocation(lighting_shader.shader_program, "model")
        # view_loc = glGetUniformLocation(lighting_shader.shader_program, "view")
        # projection_loc = glGetUniformLocation(lighting_shader.shader_program, "projection")
        #
        # # Send view projection transformations to shader
        # glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix)
        # glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection_matrix)
        #
        # light_model = Matrix44.from_translation(light_pos)
        # light_matrix = Matrix44.from_scale(Vector3([.2, .2, .2])) * light_model
        # light_matrix = np.array(light_matrix, dtype=np.float32)
        #
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, light_matrix)
        #
        # glBindVertexArray(vao[1])
        # glDrawArrays(GL_TRIANGLES, 0, 36)

        # glUseProgram(lighting_shader.shader_program)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
