from pyrr import Vector3, vector3, vector, Matrix44
from math import sin, cos
from pygame import time, mouse
import numpy as np
from math import radians
from OpenGL.GL import *


class Camera:

    def __init__(self, width, height, view):
        self.camera_position = Vector3([0., 0., 3.])
        self.camera_front = Vector3([0., 0., -1.])
        self.view_loc = view
        #self.light_view_loc = light_view

        self.sensitivity = .4
        self.last_frame = 0
        self.last_x = width / 2
        self.last_y = height / 2
        self.pitch = 0
        self.yaw = 0
        self.last_cam_y = 0

    def move_camera(self, direction):
        current_frame = time.get_ticks()
        delta_time = current_frame - self.last_frame
        camera_speed = delta_time / 20000

        if direction == "UP":
            self.camera_position[1] += camera_speed
            self.last_cam_y = self.camera_position[1]
        if direction == "DOWN":
            self.camera_position[1] -= camera_speed
            self.last_cam_y = self.camera_position[1]
        if direction == "FORWARD":
            self.camera_position += camera_speed * self.camera_front
        if direction == "BACK":
            self.camera_position -= camera_speed * self.camera_front
        if direction == "LEFT":
            self.camera_position -= vector.normalise(vector3.cross(np.array(self.camera_front, dtype=np.float32), np.array([0., 1., 0.], dtype=np.float32))) * camera_speed
        if direction == "RIGHT":
            self.camera_position += vector.normalise(vector3.cross(np.array(self.camera_front, dtype=np.float32), np.array([0., 1., 0.], dtype=np.float32))) * camera_speed
        self.camera_position[1] = self.last_cam_y

    def point_camera(self):
        pos = mouse.get_rel()
        x_offset = pos[0]
        y_offset = pos[1]

        x_offset *= self.sensitivity
        y_offset *= self.sensitivity

        self.yaw += x_offset * self.sensitivity
        self.pitch += -y_offset * self.sensitivity

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        direction_x = cos(radians(self.pitch)) * cos(radians(self.yaw))
        direction_y = sin(radians(self.pitch))
        direction_z = cos(radians(self.pitch)) * sin(radians(self.yaw))
        self.camera_front = vector.normalise(np.array([direction_x, direction_y, direction_z], dtype=np.float32))
        self.camera_front = Vector3(self.camera_front)

        view_matrix = self.look_at(self.camera_position, self.camera_position + self.camera_front)
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view_matrix)

    def look_at(self, position, target, up=Vector3([0., 1., 0.])):
        direction = vector.normalise(position - target)
        direction = np.array(direction, dtype=np.float32)
        up = np.array(up, dtype=np.float32)
        camera_right = vector.normalise(vector3.cross(up, direction))
        camera_up = vector.normalise(vector3.cross(direction, camera_right))

        translation = Matrix44.identity()
        translation[3][0] = -position[0]
        translation[3][1] = -position[1]
        translation[3][2] = -position[2]

        rotation = Matrix44.identity()
        rotation[0][0] = camera_right[0]
        rotation[1][0] = camera_right[1]
        rotation[2][0] = camera_right[2]
        rotation[0][1] = camera_up[0]
        rotation[1][1] = camera_up[1]
        rotation[2][1] = camera_up[2]
        rotation[0][2] = direction[0]
        rotation[1][2] = direction[1]
        rotation[2][2] = direction[2]

        return np.array(translation * rotation, dtype=np.float32)