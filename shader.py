import pygame
import sys
import moderngl
import numpy as np
from array import array

pygame.init()
screen = pygame.display.set_mode((800, 600))   
clock = pygame.time.Clock()
img = pygame.image.load("ninja_game/data/images/background.png")

ctx = moderngl.create_context()
quad_buffer = ctx.buffer(data=array('f', [
    -1.0, 1.0, 0.0 , 0.0, #top-left
    1.0, 1.0, 1.0 , 0.0, #top-right
    -1.0, -1.0, 0.0 , 1.0, #bottom-left
    1.0, -1.0, 1.0 , 1.0, 
    ]))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            exit()

    screen.fill((0, 0, 0))  
    screen.blit(img, (100, 100))  

    pygame.display.flip()
    clock.tick(60)      

