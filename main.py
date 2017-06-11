import glfw
import numpy as np

from OpenGL.GL import *
from shader_loader import Shader
from PIL import Image
from pyrr import Quaternion, Matrix44, Vector3, vector, vector3
from camera import Camera
from Mesh import *
from math import radians

cam = Camera()
cam_speed = .05
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

    grass_vertices = [
        0.0, 0.5, 0.0,  0.0, 0.0,
        0.0,-0.5, 0.0,  1.0, 0.0,
        1.0,-0.5, 0.0,  1.0, 1.0,

        0.0, 0.5, 0.0,  0.0, 0.0,
        1.0,-0.5, 0.0,  1.0, 1.0,
        1.0, 0.5, 0.0,  0.0, 1.0
    ]

    block_positions = [
        Vector3([0, -2, 0]),
        Vector3([1, -2, 0]),
        Vector3([-1, -2, 0]),
        Vector3([2, -2, 0]),
        Vector3([-2, -2, 0]),
        Vector3([0, -2, -1]),
        Vector3([1, -2, -1]),
        Vector3([-1, -2, -1]),
        Vector3([2, -2, -1]),
        Vector3([-2, -2, -1]),
        Vector3([1, -2, -2]),
        Vector3([2, -2, -2]),
        Vector3([0, -2, -2]),
        Vector3([-1, -2, -2]),
        Vector3([-2, -2, -2]),
        Vector3([1, -2, -3]),
        Vector3([2, -2, -3]),
        Vector3([0, -2, -3]),
        Vector3([-1, -2, -3]),
        Vector3([-2, -2, -3]),

        Vector3([-1, -1, -1]),
        Vector3([0, -1, -3])
    ]

    grass_vertices = np.array(grass_vertices, dtype=np.float32)

    glfw.init()

    window_width = 1920
    window_height = 1080
    aspect_ratio = window_width / window_height
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
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

    shader = Shader("shaders\\vertex.vs", "shaders\\fragment.fs")
    lighting_shader = Shader("shaders\\lighting_vertex.vs", "shaders\\lighting_fragment.fs")
    outline_shader = Shader("shaders\\outline_vertex.vs", "shaders\\outline_fragment.fs")

    block = ObjLoader("models\\block.obj")
    block.load_mesh()
    plane = ObjLoader("models\\grass.obj")
    plane.load_mesh()

    # Loading texture
    texture_image = Image.open("resources\\container_texture.png")
    texture_image = texture_image.transpose(Image.FLIP_TOP_BOTTOM)
    texture_data = texture_image.convert("RGBA").tobytes()

    spec_texture_image = Image.open("resources\\container_specular.png")
    spec_texture_image = spec_texture_image.transpose(Image.FLIP_TOP_BOTTOM)
    spec_texture_data = spec_texture_image.convert("RGBA").tobytes()

    grass_image = Image.open("resources\\grass.png")
    grass_image = grass_image.transpose(Image.FLIP_TOP_BOTTOM)
    grass_data = grass_image.convert("RGBA").tobytes()

    # Generating texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_image.width, texture_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Specular texture
    spec_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, spec_texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, spec_texture_image.width, spec_texture_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, spec_texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Grass texture
    grass_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, grass_texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, grass_image.width, grass_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, grass_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    last_frame = 0.0

    while not glfw.window_should_close(window):
        glfw.poll_events()
        move()

        # glClearColor(.35, .59, 1., 1.)
        glClearColor(.2, .2, .2, 1.)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        time = glfw.get_time()
        delta_time = time - last_frame
        last_frame = time

        glUseProgram(shader.shader_program)

        # Send light vec
        # shader.set_vec3("light.direction", Vector3([-.2, -1.0, -.3]))
        # shader.set_vec3("light.position", light_pos)
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
        shader.set_int("specular", 1)
        # shader.set_int("emission", 2)

        # Set view/projection matrices
        view_matrix = cam.get_view_matrix()
        view_matrix = np.array(view_matrix, dtype=np.float32)
        projection_matrix = Matrix44.perspective_projection(45.0, aspect_ratio, 0.1, 100.0)
        projection_matrix = np.array(projection_matrix, dtype=np.float32)

        # Send view projection transformations to shader
        shader.set_Matrix44f("view", view_matrix)
        shader.set_Matrix44f("projection", projection_matrix)

        # Texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, spec_texture)

        # Draw bottom
        glStencilMask(0x00)

        for each_block in range(0, len(block_positions) - 2):
            # Create model matrix
            model_matrix = Matrix44.from_scale(Vector3([1, 1, 1]))  # Scale model by 1

            model_rotation_x = Quaternion.from_x_rotation(0 * each_block)  # Rotate about x
            model_orientation_x = model_rotation_x * Quaternion()  # Create orientation matrix x
            model_rotation_y = Quaternion.from_y_rotation(0 * each_block)  # Rotate about y
            model_orientation_y = model_rotation_y * Quaternion()  # Create orientation matrix y
            model_rotation_z = Quaternion.from_z_rotation(0 * each_block)  # Rotate about z
            model_orientation_z = model_rotation_z * Quaternion()  # Create orientation matrix z

            model_translation = block_positions[each_block]
            model_translation = Matrix44.from_translation(2 * model_translation)

            model_matrix = model_matrix * model_orientation_x  # Apply orientation x
            model_matrix = model_matrix * model_orientation_y  # Apply orientation y
            model_matrix = model_matrix * model_orientation_z  # Apply orientation z
            model_matrix = model_matrix * model_translation  # Apply translation
            model_matrix = np.array(model_matrix, dtype=np.float32)  # Convert to opengl data type

            # Send model transform to shader
            shader.set_Matrix44f("model", model_matrix)
            block.draw_mesh()

        # Draw outline blocks
        glStencilFunc(GL_ALWAYS, 1, 0xFF)
        glStencilMask(0xFF)
        for each_block in range(len(block_positions) - 2, len(block_positions)):
            # Create model matrix
            model_matrix = Matrix44.from_scale(Vector3([1, 1, 1]))  # Scale model by 1

            model_rotation_x = Quaternion.from_x_rotation(0 * each_block)  # Rotate about x
            model_orientation_x = model_rotation_x * Quaternion()  # Create orientation matrix x
            model_rotation_y = Quaternion.from_y_rotation(0 * each_block)  # Rotate about y
            model_orientation_y = model_rotation_y * Quaternion()  # Create orientation matrix y
            model_rotation_z = Quaternion.from_z_rotation(0 * each_block)  # Rotate about z
            model_orientation_z = model_rotation_z * Quaternion()  # Create orientation matrix z

            model_translation = block_positions[each_block]
            model_translation = Matrix44.from_translation(2 * model_translation)

            model_matrix = model_matrix * model_orientation_x  # Apply orientation x
            model_matrix = model_matrix * model_orientation_y  # Apply orientation y
            model_matrix = model_matrix * model_orientation_z  # Apply orientation z
            model_matrix = model_matrix * model_translation  # Apply translation
            model_matrix = np.array(model_matrix, dtype=np.float32)  # Convert to opengl data type

            # Send model transform to shader
            shader.set_Matrix44f("model", model_matrix)
            block.draw_mesh()

        # Draw grass
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, grass_texture)
        model_matrix = Matrix44.from_scale(Vector3([1., 1., 1.]))
        model_translation = Matrix44.from_translation(Vector3([0., -2., 0.]))
        model_rotation_x = Quaternion.from_x_rotation(radians(-90))
        model_orientation_x = model_rotation_x * Quaternion()
        model_matrix = model_matrix * model_orientation_x
        model_matrix = model_matrix * model_translation
        model_matrix = np.array(model_matrix, dtype=np.float32)
        shader.set_Matrix44f("model", model_matrix)
        plane.draw_mesh()

        # Draw outline
        glUseProgram(outline_shader.shader_program)
        glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
        glStencilMask(0x00)
        glDisable(GL_DEPTH_TEST)

        # Send view projection transformations to shader
        outline_shader.set_Matrix44f("view", view_matrix)
        outline_shader.set_Matrix44f("projection", projection_matrix)
        for each_block in range(len(block_positions) - 2, len(block_positions)):
            # Create model matrix
            model_matrix = Matrix44.from_scale(Vector3([1.05, 1.05, 1.05]))  # Scale model by 1

            model_rotation_x = Quaternion.from_x_rotation(0 * each_block)  # Rotate about x
            model_orientation_x = model_rotation_x * Quaternion()  # Create orientation matrix x
            model_rotation_y = Quaternion.from_y_rotation(0 * each_block)  # Rotate about y
            model_orientation_y = model_rotation_y * Quaternion()  # Create orientation matrix y
            model_rotation_z = Quaternion.from_z_rotation(0 * each_block)  # Rotate about z
            model_orientation_z = model_rotation_z * Quaternion()  # Create orientation matrix z

            model_translation = block_positions[each_block]
            model_translation = Matrix44.from_translation(2 * model_translation)

            model_matrix = model_matrix * model_orientation_x  # Apply orientation x
            model_matrix = model_matrix * model_orientation_y  # Apply orientation y
            model_matrix = model_matrix * model_orientation_z  # Apply orientation z
            model_matrix = model_matrix * model_translation  # Apply translation
            model_matrix = np.array(model_matrix, dtype=np.float32)  # Convert to opengl data type

            # Send model transform to shader
            outline_shader.set_Matrix44f("model", model_matrix)
            block.draw_mesh()

        glStencilMask(0xFF)
        glEnable(GL_DEPTH_TEST)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
