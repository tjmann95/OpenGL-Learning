import numpy as np
from OpenGL.GL import *
from pyrr import Vector3
from TerrainGen import HillGrid
from pprint import pprint


class ObjLoader:

    def __init__(self, file, type):
        self.vert_coords = []
        self.text_coords = []
        self.norm_coords = []

        self.vertex_index = []
        self.texture_index = []
        self.normal_index = []

        self.filepath = file
        self.num_objects = 0
        self.type = type
        if self.type == "block":
            self.indices = 36
        elif self.type == "plane":
            self.indices = 6

        self.model = []

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

    def load_model(self, file):
        for line in open(file, 'r'):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'v':
                self.vert_coords.append(values[1:4])
            if values[0] == 'vt':
                self.text_coords.append(values[1:3])
            if values[0] == 'vn':
                self.norm_coords.append(values[1:4])

            if values[0] == 'f':
                face_i = []
                text_i = []
                norm_i = []
                for v in values[1:4]:
                    w = v.split('/')
                    face_i.append(int(w[0])-1)
                    text_i.append(int(w[1])-1)
                    norm_i.append(int(w[2])-1)
                self.vertex_index.append(face_i)
                self.texture_index.append(text_i)
                self.normal_index.append(norm_i)

        self.vertex_index = [y for x in self.vertex_index for y in x]
        self.texture_index = [y for x in self.texture_index for y in x]
        self.normal_index = [y for x in self.normal_index for y in x]

        for i in self.vertex_index:
            self.model.extend(self.vert_coords[i])

        for i in self.texture_index:
            self.model.extend(self.text_coords[i])

        for i in self.normal_index:
            self.model.extend(self.norm_coords[i])

        self.model = np.array(self.model, dtype='float32')

    def load_mesh(self):
        obj = ObjLoader(self.filepath, self.type)
        obj.load_model(self.filepath)

        texture_offset = len(obj.vertex_index) * 12
        normal_offset = texture_offset + len(obj.texture_index) * 8

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(GL_ARRAY_BUFFER, obj.model.itemsize * len(obj.model), obj.model, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, obj.model.itemsize * 2, ctypes.c_void_p(texture_offset))
        glEnableVertexAttribArray(1)

        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(normal_offset))
        glEnableVertexAttribArray(2)

        self.instance_buffers()
        glBindVertexArray(0)

    def draw_mesh(self):
        glBindVertexArray(self.vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, self.indices, self.num_objects)
        glBindVertexArray(0)

    def set_locations(self):
        # instance_array = []
        # offset = 0
        #
        # for z in range(0, 100, 4):
        #     for y in range(0, 100, 4):
        #         for x in range(0, 100, 4):
        #             translation = Vector3([0.0, 0.0, 0.0])
        #             translation.x = x + offset
        #             translation.y = y + offset
        #             translation.z = z + offset
        #             instance_array.append(translation)
        #
        # instance_array = np.array(instance_array, np.float32).flatten()
        # self.num_objects = int(len(instance_array) / 3)
        size = 200
        terrain = HillGrid(KRADIUS=.08, ITER=100, SIZE=size).__getitem__()
        print(terrain)
        instance_array = []

        for x in range(0, size):
            for y in range(0, size):
                instance_array.append([x, terrain[x][y], y])
        instance_array = np.array(instance_array, np.float32).flatten()
        self.num_objects = int(len(instance_array) / 3)

        return instance_array

    def instance_buffers(self):
        instance_array = self.set_locations()

        instanceVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
        glBufferData(GL_ARRAY_BUFFER, instance_array.itemsize * len(instance_array), instance_array, GL_STATIC_DRAW)

        glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(5)
        glVertexAttribDivisor(5, 1)
