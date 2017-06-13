import glfw
import numpy as np

from OpenGL.GL import *
from shader_loader import Shader
from PIL import Image
from pyrr import Quaternion, Matrix44, Vector3, Matrix33
from camera import Camera
from Mesh import *
from math import radians
from texture_loader import Texture

cam = Camera()
cam_speed = .05
delta_time = 0
last_x, last_y = 400, 400
first_mouse = True
keys = [False] * 1024

light_pos = Vector3([0.0, 0.0, 3.0])

point_light_positions = [
    Vector3([.7, .2, 2.0]),
    Vector3([2.3, -3.3, -4.0]),
    Vector3([-4.0, 2.0, -12.0]),
    Vector3([0.0, 0.0, -3.0])
]

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
        cam.process_keyboard("FORWARD", cam_speed * delta_time)
    if keys[glfw.KEY_S]:
        cam.process_keyboard("BACKWARD", cam_speed * delta_time)
    if keys[glfw.KEY_A]:
        cam.process_keyboard("LEFT", cam_speed * delta_time)
    if keys[glfw.KEY_D]:
        cam.process_keyboard("RIGHT", cam_speed * delta_time)
    if keys[glfw.KEY_SPACE]:
        cam.process_keyboard("UP", cam_speed * delta_time)
    if keys[glfw.KEY_LEFT_SHIFT]:
        cam.process_keyboard("DOWN", cam_speed * delta_time)


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


def load_cubemap(locations):
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)

    for i in range(0, len(locations), 1):
        cubemap_image = Image.open(locations[i])
        cubemap_data = cubemap_image.convert("RGBA").tobytes()

        if cubemap_data:
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                         0, GL_RGBA, cubemap_image.width, cubemap_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, cubemap_data)
        else:
            raise Exception("Cubemap texture failed to load at path: " + locations[i])

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    return tex_id


def main():

    skybox_vertices = [
        -1.0, 1.0, -1.0,
        -1.0, -1.0, -1.0,
        1.0, -1.0, -1.0,
        1.0, -1.0, -1.0,
        1.0, 1.0, -1.0,
        -1.0, 1.0, -1.0,

        -1.0, -1.0, 1.0,
        -1.0, -1.0, -1.0,
        -1.0, 1.0, -1.0,
        -1.0, 1.0, -1.0,
        -1.0, 1.0, 1.0,
        -1.0, -1.0, 1.0,

        1.0, -1.0, -1.0,
        1.0, -1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, -1.0,
        1.0, -1.0, -1.0,

        -1.0, -1.0, 1.0,
        -1.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, -1.0, 1.0,
        -1.0, -1.0, 1.0,

        -1.0, 1.0, -1.0,
        1.0, 1.0, -1.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        -1.0, 1.0, 1.0,
        -1.0, 1.0, -1.0,

        -1.0, -1.0, -1.0,
        -1.0, -1.0, 1.0,
        1.0, -1.0, -1.0,
        1.0, -1.0, -1.0,
        -1.0, -1.0, 1.0,
        1.0, -1.0, 1.0
    ]

    skybox_vertices = np.array(skybox_vertices, dtype=np.float32)

    framebuffer_vertices = [
        -1.0,  1.0, 0.0, 1.0,
        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
        -1.0,  1.0, 0.0, 1.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0
    ]

    framebuffer_vertices = np.array(framebuffer_vertices, dtype=np.float32)

    offset = 2
    block_positions = []
    for y in range(-10, 10, 2):
        for x in range(-10, 10, 2):
            translation = Vector3([x + offset, y + offset, 0], dtype=np.float32)
            block_positions.append(translation)

    glfw.init()

    window_width = 1920
    window_height = 1080
    aspect_ratio = window_width / window_height
    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(window_width, window_height, "Learning", glfw.get_primary_monitor(), None)
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

    glEnable(GL_STENCIL_TEST)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)
    glFrontFace(GL_CW)

    shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs")
    lighting_shader = Shader("shaders\\lighting_vertex.vs", "shaders\\lighting_fragment.fs")
    outline_shader = Shader("shaders\\outline_vertex.vs", "shaders\\outline_fragment.fs")
    skybox_shader = Shader("shaders\\skybox_vertex.vs", "shaders\\skybox_fragment.fs")
    screen_shader = Shader("shaders\\framebuffer_vertex.vs", "shaders\\framebuffer_fragment.fs")

    block = ObjLoader("models\\block.obj", "block")
    block.load_mesh()
    plane = ObjLoader("models\\grass.obj", "plane")
    plane.load_mesh()

    # Skybox buffers
    skybox_vao = glGenVertexArrays(1)
    skybox_vbo = glGenBuffers(1)
    glBindVertexArray(skybox_vao)
    glBindBuffer(GL_ARRAY_BUFFER, skybox_vbo)
    glBufferData(GL_ARRAY_BUFFER, skybox_vertices.nbytes, skybox_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * skybox_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Framebuffer buffers
    framebuffer_vao = glGenVertexArrays(1)
    framebuffer_vbo = glGenBuffers(1)
    glBindVertexArray(framebuffer_vao)
    glBindBuffer(GL_ARRAY_BUFFER, framebuffer_vbo)
    glBufferData(GL_ARRAY_BUFFER, framebuffer_vertices.nbytes, framebuffer_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * framebuffer_vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * framebuffer_vertices.itemsize, ctypes.c_void_p(2))
    glEnableVertexAttribArray(1)

    glUseProgram(screen_shader.shader_program)
    screen_shader.set_int("screenTexture", 0)

    # Generating texture
    container = Texture("resources\\cobblestone_texture.png", True).tex_ID

    # Framebuffer
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    tex_color_buffer = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_color_buffer)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, window_width, window_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_color_buffer, 0)

    # Renderbuffer
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, window_width, window_height)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("ERROR: FRAMEBUFFER: Framebuffer is not complete!")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Cubemap
    skybox = [
        "resources\\right.jpg",
        "resources\\left.jpg",
        "resources\\top.jpg",
        "resources\\bottom.jpg",
        "resources\\back.jpg",
        "resources\\front.jpg"
    ]
    cubemap = load_cubemap(skybox)

    last_frame = 0.0

    while not glfw.window_should_close(window):
        global delta_time
        glfw.poll_events()
        move()

        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        glClearColor(.1, .1, .1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        time = glfw.get_time()
        delta_time = (time - last_frame) * 200
        last_frame = time

        # Set view/projection matrices
        view_matrix = cam.get_view_matrix()
        view_matrix = np.array(view_matrix, dtype=np.float32)
        projection_matrix = Matrix44.perspective_projection(45.0, aspect_ratio, 0.1, 500.0)
        projection_matrix = np.array(projection_matrix, dtype=np.float32)

        glUseProgram(shader.shader_program)

        # Send view pos
        shader.set_vec3("viewPos", cam.camera_pos)

        # Send light to shader
        shader.set_vec3("dirLight.direction", Vector3([-.2, -1.0, -.3]))
        shader.set_vec3("dirLight.ambient", Vector3([.05, .05, .05]))
        shader.set_vec3("dirLight.diffuse", Vector3([.4, .4, .4]))
        shader.set_vec3("dirLight.specular", Vector3([.5, .5, .5]))

        shader.set_vec3("pointLights[0].position", point_light_positions[0])
        shader.set_vec3("pointLights[0].ambient", Vector3([.05, .05, .05]))
        shader.set_vec3("pointLights[0].diffuse", Vector3([.8, .8, .8]))
        shader.set_vec3("pointLights[0].specular", Vector3([1.0, 1.0, 1.0]))
        shader.set_float("pointLights[0].constant", 1.0)
        shader.set_float("pointLights[0].linear", .09)
        shader.set_float("pointLights[0].quadratic", .032)

        shader.set_vec3("pointLights[1].position", point_light_positions[1])
        shader.set_vec3("pointLights[1].ambient", Vector3([.05, .05, .05]))
        shader.set_vec3("pointLights[1].diffuse", Vector3([.8, .8, .8]))
        shader.set_vec3("pointLights[1].specular", Vector3([1.0, 1.0, 1.0]))
        shader.set_float("pointLights[1].constant", 1.0)
        shader.set_float("pointLights[1].linear", .09)
        shader.set_float("pointLights[1].quadratic", .032)

        shader.set_vec3("pointLights[2].position", point_light_positions[2])
        shader.set_vec3("pointLights[2].ambient", Vector3([.05, .05, .05]))
        shader.set_vec3("pointLights[2].diffuse", Vector3([.8, .8, .8]))
        shader.set_vec3("pointLights[2].specular", Vector3([1.0, 1.0, 1.0]))
        shader.set_float("pointLights[2].constant", 1.0)
        shader.set_float("pointLights[2].linear", .09)
        shader.set_float("pointLights[2].quadratic", .032)

        shader.set_vec3("pointLights[3].position", point_light_positions[3])
        shader.set_vec3("pointLights[3].ambient", Vector3([.05, .05, .05]))
        shader.set_vec3("pointLights[3].diffuse", Vector3([.8, .8, .8]))
        shader.set_vec3("pointLights[3].specular", Vector3([1.0, 1.0, 1.0]))
        shader.set_float("pointLights[3].constant", 1.0)
        shader.set_float("pointLights[3].linear", .09)
        shader.set_float("pointLights[3].quadratic", .032)

        # Send material to shader
        shader.set_float("material.shininess", 32.0)

        # Send maps to shader
        shader.set_int("diffuse", 0)

        # Send view, projection transformations to shader
        shader.set_Matrix44f("view", view_matrix)
        shader.set_Matrix44f("projection", projection_matrix)

        # Texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, container)

        # Draw block
        block.draw_mesh()

        # Draw grass
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, grass_texture)
        # model_matrix = Matrix44.from_scale(Vector3([1., 1., 1.]))
        # model_translation = Matrix44.from_translation(Vector3([0., -2., 0.]))
        # model_rotation_x = Quaternion.from_x_rotation(radians(-90))
        # model_orientation_x = model_rotation_x * Quaternion()
        # model_matrix = model_matrix * model_orientation_x
        # model_matrix = model_matrix * model_translation
        # model_matrix = np.array(model_matrix, dtype=np.float32)
        # shader.set_Matrix44f("model", model_matrix)
        # plane.draw_mesh()

        # Draw outline
        # glUseProgram(outline_shader.shader_program)
        # glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
        # glStencilMask(0x00)
        # glDisable(GL_DEPTH_TEST)
        #
        # # Send view projection transformations to shader
        # outline_shader.set_Matrix44f("view", view_matrix)
        # outline_shader.set_Matrix44f("projection", projection_matrix)
        # for each_block in range(len(block_positions) - 2, len(block_positions)):
        #     # Create model matrix
        #     model_matrix = Matrix44.from_scale(Vector3([1.05, 1.05, 1.05]))  # Scale model by 1
        #
        #     model_rotation_x = Quaternion.from_x_rotation(0 * each_block)  # Rotate about x
        #     model_orientation_x = model_rotation_x * Quaternion()  # Create orientation matrix x
        #     model_rotation_y = Quaternion.from_y_rotation(0 * each_block)  # Rotate about y
        #     model_orientation_y = model_rotation_y * Quaternion()  # Create orientation matrix y
        #     model_rotation_z = Quaternion.from_z_rotation(0 * each_block)  # Rotate about z
        #     model_orientation_z = model_rotation_z * Quaternion()  # Create orientation matrix z
        #
        #     model_translation = block_positions[each_block]
        #     model_translation = Matrix44.from_translation(2 * model_translation)
        #
        #     model_matrix = model_matrix * model_orientation_x  # Apply orientation x
        #     model_matrix = model_matrix * model_orientation_y  # Apply orientation y
        #     model_matrix = model_matrix * model_orientation_z  # Apply orientation z
        #     model_matrix = model_matrix * model_translation  # Apply translation
        #     model_matrix = np.array(model_matrix, dtype=np.float32)  # Convert to opengl data type
        #
        #     # Send model transform to shader
        #     outline_shader.set_Matrix44f("model", model_matrix)
        #     block.draw_mesh()
        #
        # glStencilMask(0xFF)
        # glEnable(GL_DEPTH_TEST)

        # Draw skybox
        glDepthFunc(GL_LEQUAL)
        glUseProgram(skybox_shader.shader_program)
        view_matrix = Matrix44(Matrix33.from_matrix44(view_matrix))
        view_matrix = np.array(view_matrix, dtype=np.float32)
        skybox_shader.set_int("skybox", 0)
        skybox_shader.set_Matrix44f("view", view_matrix)
        skybox_shader.set_Matrix44f("projection", projection_matrix)
        glBindVertexArray(skybox_vao)
        glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDisable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(screen_shader.shader_program)
        glBindVertexArray(framebuffer_vao)
        glBindTexture(GL_TEXTURE_2D, tex_color_buffer)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
