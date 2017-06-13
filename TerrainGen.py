import numpy as np
from noise import *


class Terrain:

    def __init__(self, sizeX, sizeY):

        self.width = sizeX
        self.depth = sizeY

    def get_map(self):
        terrain = np.zeros((self.width, self.depth))
        for x in range(0, self.width):
            for y in range(0, self.depth):
                terrain[x][y] = pnoise2(x, y)

        return terrain
