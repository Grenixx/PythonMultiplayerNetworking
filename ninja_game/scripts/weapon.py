import pygame

class Lance:
    """Classe gérant une arme de type lance."""
    def __init__(self, owner):
        self.owner = owner
        self.image = owner.game.assets['lance']
        self.angle = 0
        self.attack_duration = 15
        self.attack_timer = 0
        self.attack_direction = 'front'

    def update(self):
        if self.attack_timer > 0:
            self.attack_timer = max(0, self.attack_timer - 1)

    def rect(self):
        pos = self.get_render_pos((0, 0))
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        return rotated_image.get_rect(topleft=pos)

    def get_render_pos(self, offset):
        center_x = self.owner.rect().centerx - offset[0]
        center_y = self.owner.rect().centery - offset[1]

        progress = (self.attack_duration - self.attack_timer) / self.attack_duration
        max_thrust = 16
        retract_distance = 4
        
        if progress < 0.3:
            thrust_progress = progress / 0.3
        elif progress < 0.6:
            thrust_progress = 1.0
        else:
            thrust_progress = 1.0 - ((progress - 0.6) / 0.4)

        thrust = thrust_progress * max_thrust - retract_distance
        rotated_image = pygame.transform.rotate(self.image, self.angle)

        if self.attack_direction == 'up':
            pos_x = center_x - rotated_image.get_width() // 2
            pos_y = center_y - rotated_image.get_height() - thrust
        elif self.attack_direction == 'down':
            pos_x = center_x - rotated_image.get_width() // 2
            pos_y = center_y + thrust
        else:
            pos_y = center_y - rotated_image.get_height() // 2
            if self.owner.flip:
                pos_x = center_x - rotated_image.get_width() - thrust + 15
            else:
                pos_x = center_x + thrust - 15

        return (pos_x, pos_y)

    def render(self, surf, offset=(0, 0)):
        if self.attack_timer > 0:
            pos = self.get_render_pos(offset)
            rotated_image = pygame.transform.rotate(self.image, self.angle)
            surf.blit(rotated_image, pos)
            # hitbox debug
            hitbox = self.rect()
            pygame.draw.rect(surf, (255, 0, 0),
                             pygame.Rect(hitbox.x - offset[0], hitbox.y - offset[1],
                                         hitbox.width, hitbox.height), 2)

    def swing(self, direction):
        self.attack_timer = self.attack_duration
        self.attack_direction = direction if direction in ['up', 'down'] else 'front'

        if direction == 'up':
            self.angle = 90
        elif direction == 'down':
            self.angle = -90
        else:
            self.angle = 180 if self.owner.flip else 0
        print(f"Swing direction: {direction}, Player flip: {self.owner.flip}, Final angle: {self.angle}")


class Mace:
    """Classe gérant une arme de type masse."""
    def __init__(self, owner):
        self.owner = owner
        original_animation = owner.game.assets['mace'].copy()
        scaled_images = []
        for img in original_animation.images:
            scaled_images.append(pygame.transform.scale(img, (img.get_width() // 4, img.get_height() // 4)))
        self.animation = owner.game.assets['mace'].__class__(scaled_images, original_animation.img_duration, original_animation.loop)
        self.attack_timer = 0

    def update(self):
        if self.attack_timer > 0:
            self.attack_timer = max(0, self.attack_timer - 1)
            self.animation.update()

    def rect(self):
        pos = self.get_render_pos((0, 0))
        current_image = self.animation.img()
        return pygame.Rect(pos[0], pos[1], current_image.get_width(), current_image.get_height())

    def get_render_pos(self, offset):
        center_x = self.owner.rect().centerx - offset[0]
        center_y = self.owner.rect().centery - offset[1]
        image_to_render = self.animation.img()
        pos_y = center_y - image_to_render.get_height() // 2 - 10
        pos_x = center_x - image_to_render.get_width() if self.owner.flip else center_x
        return (pos_x, pos_y)

    def render(self, surf, offset=(0, 0)):
        if self.attack_timer > 0:
            image_to_render = self.animation.img()
            image_to_render = pygame.transform.flip(image_to_render, self.owner.flip, False)
            pos = self.get_render_pos(offset)
            surf.blit(image_to_render, pos)

    def swing(self, direction):
        self.attack_timer = self.animation.img_duration * len(self.animation.images)
        self.animation.frame = 0


class Weapon:
    """Classe qui gère l'arme actuellement équipée par le joueur."""
    def __init__(self, owner, weapon_type='lance'):
        self.owner = owner
        if weapon_type == 'lance':
            self.weapon_equiped = Lance(owner)
        elif weapon_type == 'mace':
            self.weapon_equiped = Mace(owner)
        else:
            self.weapon_equiped = Lance(owner)
