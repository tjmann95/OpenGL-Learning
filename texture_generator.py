import pygame
import os
from sys import exit

pygame.init()

path = "resources\\leaves_oak.png"

texture_image = pygame.image.load(path)

size = texture_image.get_rect().size[0] * 4
name = path[path.rfind("\\") + 1:]
name = name.split(".")
new_name = name[0] + "_texture." + name[1]

surface = pygame.display.set_mode([size, size])
surface.fill([0, 0, 0])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.image.save(surface, new_name)
            os.rename("E:\\Programming\\Projects\\OpenGL-Learning-master\\" + new_name, "E:\\Programming\\Projects\\OpenGL-Learning-master\\resources\\" + new_name)
            pygame.quit()
            exit()

    surface.blit(texture_image, (size - size / 4, size - size /4))
    surface.blit(texture_image, (size - size / 4, size - 2 * size / 4))
    surface.blit(texture_image, (size - size / 4, size - 3 * size / 4))

    surface.blit(texture_image, (size - 2 * size / 4, size - 2 * size / 4))
    surface.blit(texture_image, (size - 3 * size / 4, size - 2 * size / 4))
    surface.blit(texture_image, (size - 4 * size / 4, size - 2 * size / 4))

    pygame.display.update()
