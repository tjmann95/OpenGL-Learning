from OpenGL.GL import *

class Shader(object):

    def __init__(self, vertex, fragment):
        self.vertex_path = vertex
        self.fragment_path = fragment

        self.shader_program = self.compile_shader()

    def load_source(self, file):
        f = open(file, "r")
        source = f.read()
        f.close()

        return source

    def compile_shader(self):
        vertex_shader_source = self.load_source(self.vertex_path)
        fragment_shader_source = self.load_source(self.fragment_path)

        # Compile vertex shader
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)

        # Check vertex compilation success
        error_message = glGetShaderInfoLog(vertex_shader)
        if not "No errors." in str(error_message):
            print("ERROR: Vertex shader failed to compile:\n" + str(error_message))

        # Compile fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)

        # Check fragment compilation success
        error_message = glGetShaderInfoLog(fragment_shader)
        if not "No errors." in str(error_message):
            print("ERROR: Fragment shader failed to compile:\n" + str(error_message))

        # Creating shader program
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)

        # Check shader program success
        error_message = glGetProgramInfoLog(shader_program)
        if not "No errors." in str(error_message):
            print("ERROR: Shader program failed:\n" + str(error_message))

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program
