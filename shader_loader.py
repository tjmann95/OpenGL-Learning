from OpenGL.GL import *
import OpenGL.GL.shaders


class Shader(object):

    def __init__(self, vertex, fragment):
        self.vertex_shader_file = vertex
        self.fragment_shader_file = fragment

        self.shader_program = self.compile_shader(self.vertex_shader_file, self.fragment_shader_file)

    def load_shader(self, file):
        shader_source = ""
        with open(file) as f:
            shader_source = f.read()
        f.close()
        return str.encode(shader_source)

    def compile_shader(self, vs, fs):
        vert_shader = self.load_shader(vs)
        frag_shader = self.load_shader(fs)

        vertex_shader = OpenGL.GL.shaders.compileShader(vert_shader, GL_VERTEX_SHADER)
        fragment_shader = OpenGL.GL.shaders.compileShader(frag_shader, GL_FRAGMENT_SHADER)
        shader_program = OpenGL.GL.shaders.compileProgram(vertex_shader, fragment_shader)

        return shader_program

    def use(self): glUseProgram(self.shader_program)
