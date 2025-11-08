import random
from math import *
import pygame  # facultatif, pour debug visuel

class EnemyManager:
    def __init__(self, tilemap, num_enemies=1, speed=1.0):
        self.tilemap = tilemap
        self.enemies = {}
        self.next_enemy_id = 1
        self.speed = speed
        self.create_blob(num_enemies)

    def create_blob(self, num):
        for _ in range(num):
            eid = self.next_enemy_id
            self.next_enemy_id += 1
            self.enemies[eid] = {
                'x': 50,
                'y': 50,
                'vx': 0.0,
                'vy': 0.0,
                'target_player': None,
            }
        print(f"{num} ennemis créés !")

    def update(self, players, screen=None):
        """Met à jour tous les ennemis en fonction de la map et des joueurs"""
        if not players:
            return

        for eid, enemy in self.enemies.items():
            pos = [enemy['x'], enemy['y']]

            # --- Trouver le joueur le plus proche ---
            closest_pid, closest_dist = None, None
            for pid, ppos in players.items():
                dist = distance_squared_to(pos, ppos)
                if closest_pid is None or dist < closest_dist:
                    closest_pid, closest_dist = pid, dist

            if closest_pid is None:
                continue

            player_pos = players[closest_pid]
            to_player = normalized(vector_to(pos, player_pos))

            # --- Raycasts pour éviter les obstacles ---
            avoid_vec = [0.0, 0.0]
            num_rays = 9
            fov = radians(90)  # champ de vision 90°
            ray_length = 10

            main_angle = angle(to_player)

            for i in range(num_rays):
                # Rayons répartis autour du joueur
                offset = (i - num_rays // 2) * (fov / num_rays)
                ray_angle = main_angle + offset

                hit_dist = raycast_distance(pos, ray_angle, self.tilemap, ray_length, 4)
                color = (100, 100, 100)

                if hit_dist is not None:
                    # plus l’obstacle est proche → plus la poussée est forte
                    strength = 1 - (hit_dist / ray_length)
                    push = vec_from_angle(strength, ray_angle + pi)
                    avoid_vec = add_vecs(avoid_vec, push)
                    color = (255, 0, 0)

                # --- Dessin visuel du raycast ---
                if screen:
                    ray_end = add_vecs(pos, vec_from_angle(ray_length, ray_angle))
                    pygame.draw.line(screen, color, pos, ray_end, 1)

            # --- Combinaison des forces ---
            move_dir = add_vecs(to_player, avoid_vec)
            if norm(move_dir) > 0:
                move_dir = normalized(move_dir)

            step = [move_dir[0] * self.speed, move_dir[1] * self.speed]

            # --- Test collision simple ---
            new_x = pos[0] + step[0]
            new_y = pos[1] + step[1]

            if not self.tilemap.solid_check((new_x, pos[1])):
                enemy['x'] = new_x
            if not self.tilemap.solid_check((pos[0], new_y)):
                enemy['y'] = new_y

# ==========================================================
# --- Fonctions utilitaires ---
# ==========================================================

def add_vecs(a, b):
    return [a[0] + b[0], a[1] + b[1]]

def sub_vecs(a, b):
    return [a[0] - b[0], a[1] - b[1]]

def vector_to(a, b):
    return [b[0] - a[0], b[1] - a[1]]

def distance_squared_to(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return dx * dx + dy * dy

def distance_to(a, b):
    return sqrt(distance_squared_to(a, b))

def norm(v):
    return sqrt(v[0] ** 2 + v[1] ** 2)

def normalized(v):
    n = norm(v)
    if n == 0:
        return [0, 0]
    return [v[0] / n, v[1] / n]

def vec_from_angle(length, angle):
    return [cos(angle) * length, sin(angle) * length]

def angle(v):
    return atan2(v[1], v[0])

# ==========================================================
# --- Raycasting ---
# ==========================================================

def raycast_collide(pos, angle, tilemap, dist_max=100, step=4, mask=[]):
    """Renvoie True si le rayon touche un obstacle"""
    vec = vec_from_angle(step, angle)
    pos_check = list(pos)
    dist = 0
    while dist <= dist_max:
        check_type = tilemap.check_type((pos_check[0], pos_check[1]))
        if (mask == [] and check_type is not None) or (check_type in mask):
            return True
        pos_check = add_vecs(pos_check, vec)
        dist += step
    return False

def raycast_distance(pos, angle, tilemap, dist_max=100, step=4, mask=[]):
    """Renvoie la distance jusqu’à l’obstacle le plus proche (ou None)"""
    vec = vec_from_angle(step, angle)
    pos_check = list(pos)
    dist = 0
    while dist <= dist_max:
        check_type = tilemap.check_type((pos_check[0], pos_check[1]))
        if (mask == [] and check_type is not None) or (check_type in mask):
            return dist
        pos_check = add_vecs(pos_check, vec)
        dist += step
    return None
