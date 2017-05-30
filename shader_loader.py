from OpenGL.GL import *
import OpenGL.GL.shaders


class Shader(object):

    def __init__(self, vertex, fragment):
        self.vertex_shader_file = vertex
        self.fragment_shader_file = fragment

        self.compile_shader()

    def load_shader(self, file):
        # shader_source = ""
        with open(file) as f:
            shader_source = f.read()
        f.close()
        return str.encode(shader_source)

    def compile_shader(self):
        vert_shader = self.load_shader(self.vertex_shader_file)
        frag_shader = self.load_shader(self.fragment_shader_file)

        # Compile vertex shader
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, 1, vert_shader, None)
        glCompileShader(vertex_shader)

        # Check vertex compilation success
        vert_success = 0
        vert_info_log = ""
        glGetShaderiv(vertex_shader, GL_COMPILE_STATUS, vert_success)
        if not vert_success:
            glGetShaderInfoLog(vertex_shader, 512, None, vert_info_log)
            print("ERROR: Vertex shader failed to compile:\n" + vert_info_log)

        # Compile fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, 1, frag_shader, None)
        glCompileShader(fragment_shader)

        # Check fragment compilation success
        frag_success = 0
        frag_info_log = ""
        glGetShaderiv(fragment_shader, 512, None, frag_info_log)
        if not frag_success:
            glGetShaderInfoLog(fragment_shader, 512, None, frag_info_log)
            print("ERROR: Fragment shader failed to compile:\n" + frag_info_log)

        # Creating shader program
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)

        # Check shader program success
        program_success = 0
        program_info_log = ""
        glGetProgramiv(shader_program, GL_LINK_STATUS, program_success)
        if not program_success:
            glGetProgramInfoLog(shader_program, 512, None, program_info_log)
            print("ERROR: Shader program failed:\n" + program_info_log)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program
