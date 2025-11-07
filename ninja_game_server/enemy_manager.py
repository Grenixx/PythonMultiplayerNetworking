import random

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

            # --- Gravité ---
            #if not self.tilemap.solid_check((ex, ey + 4)):
            #    enemy['vy'] += 0.3  # tombe
            #else:
             #   enemy['vy'] = 0

            # --- Trouver la cible la plus proche ---
            enemy['target_player'] = closest_pid


            # --- Test collisions map ---

                enemy['x'] = new_x
            else:

                enemy['y'] = new_y
            else:
                enemy['vy'] = 0

            # Limites de la map
            enemy['x'] = max(0, min(enemy['x'], 1000))
            enemy['y'] = max(0, min(enemy['y'], 1000))
