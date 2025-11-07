import random
from math import *

class EnemyManager:
    def __init__(self, tilemap, num_enemies=20, speed=0.5):
        self.tilemap = tilemap
        self.enemies = {}
        self.next_enemy_id = 1
        self.speed = speed
        self.create_enemies(num_enemies)

    def create_enemies(self, num):
        for _ in range(num):
            eid = self.next_enemy_id
            self.next_enemy_id += 1
            self.enemies[eid] = {
                'x': random.uniform(50, 250),
                'y': random.uniform(50, 250),
                'vx': 0.0,
                'vy': 0.0,
                'target_player': None,
            }
        print(f"{num} ennemis créés !")

    def update(self, players):
        """Met à jour tous les ennemis en fonction de la map et des joueurs"""
        if not players:
            return

        for eid, enemy in self.enemies.items():
            pos = [enemy['x'], enemy['y']]

            # --- Gravité ---
            #if not self.tilemap.solid_check((ex, ey + 4)):
            #    enemy['vy'] += 0.3  # tombe
            #else:
             #   enemy['vy'] = 0

            # --- Trouver la cible la plus proche ---
            closest_dist = None
            closest_pid = None
            for pid in players.keys():
                dist = distance_squared_to(pos, players[pid])
                if closest_dist == None or closest_dist > dist:
                    closest_dist,closest_pid = dist,pid

            enemy['target_player'] = closest_pid

            step = [0,0]
            dist = distane_to(pos, players[closest_pid])
            if dist > 1:
                step = normalized(vector_to(pos, players[closest_pid]))
                step = [i * self.speed for i in step]

            # --- Test collisions map ---
            new_x = pos[0] + step[0]
            new_y = pos[1] + step[1]

            if not self.tilemap.solid_check((new_x, pos[1])):
                enemy['x'] = new_x
            else:
                enemy['vx'] = 0

            if not self.tilemap.solid_check((pos[0], new_y)):
                enemy['y'] = new_y
            else:
                enemy['vy'] = 0

            # Limites de la map
            enemy['x'] = max(0, min(enemy['x'], 1000))
            enemy['y'] = max(0, min(enemy['y'], 1000))

def vector_to(pos1: list,pos2: list):
    """
    Renvoie un vecteur de la position 1 vers 2
    """
    return [pos2[0] - pos1[0], pos2[1] - pos1[1]]

def distance_squared_to(pos1: list,pos2: list):
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

def distane_to(pos1: list,pos2: list):
    return sqrt(distance_squared_to(pos1,pos2))

def normalized(vec: list):
    norm = distane_to([0,0],vec)
    vec = [i/norm for i in vec]
    return vec

def is_normalized(vec: list):
    return vec == normalized(vec)