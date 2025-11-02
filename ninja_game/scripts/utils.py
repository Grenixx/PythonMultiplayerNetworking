import os
import pygame

# Dossier racine du projet (le dossier "ninja_game")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_IMG_PATH = os.path.join(BASE_DIR, 'data', 'images')

def load_image(path):
    # 🔧 CORRECTION : toujours utiliser os.path.join, pas "+"
    full_path = os.path.join(BASE_IMG_PATH, path)
    img = pygame.image.load(full_path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    folder_path = os.path.join(BASE_IMG_PATH, path)
    for img_name in sorted(os.listdir(folder_path)):
        # 🔧 CORRECTION : ici aussi, join pour garder un chemin propre
        images.append(load_image(os.path.join(path, img_name)))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
