import random
import math


class HillGrid:
    def __init__(self, KRADIUS=(1.0 / 5.0), ITER=200, SIZE=40):
        self.kradius = KRADIUS
        self.iter = ITER
        self.size = SIZE

        self.grid = [[0 for x in range(self.size)] for y in range(self.size)]

        self.max = self.size * self.kradius/2
        for i in range(self.iter):
            self.step()

    def dump(self):
        for element in self.grid:
            s = ""
            for alo in element:
                s += "%s " % str(alo)
            print(s)

    def __getitem__(self):
        return self.grid

    def step(self):
        point = [random.randint(0, self.size - 1), random.randint(0, self.size - 1)]
        radius = random.uniform(0, self.max)

        start_x = point[0] - radius / 2
        start_y = point[1] - radius / 2

        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0

        x2 = point[0]
        y2 = point[1]

        for x in range(self.size):
            for y in range(self.size):
                z = radius ** 2 - (math.pow(x2 - x, 2) + math.pow(y2 - y, 2))
                if z >= 0:
                    self.grid[x][y] += int(z)


if __name__ == "__main__":
    h = HillGrid(ITER=50, SIZE=20)
    terrainGrid = h.__getitem__()
    flat = [x for sublist in terrainGrid for x in sublist]
    pprint(terrainGrid)
    blocks = []

    for y in range(0, 20):
        for x in range(0, 20):
            blocks.append([x, y, terrainGrid[y][x]])

    print(blocks)