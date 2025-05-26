import pygame
import os
pygame.init()
print(pygame.image.get_extended())
folder_path = 'current_images/'
print(sorted(os.listdir(folder_path)))
#pygame.image.load("current_images/id145_text_.jpg")