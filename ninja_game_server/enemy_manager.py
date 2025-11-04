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
            ex, ey = enemy['x'], enemy['y']

            # --- Gravité ---
            #if not self.tilemap.solid_check((ex, ey + 4)):
            #    enemy['vy'] += 0.3  # tombe
            #else:
             #   enemy['vy'] = 0

            # --- Trouver la cible la plus proche ---
            closest_pid = min(
                players,
                key=lambda pid: (players[pid][0] - ex) ** 2 + (players[pid][1] - ey) ** 2
            )
            enemy['target_player'] = closest_pid
            px, py, _, _ = players[closest_pid]

            dx, dy = px - ex, py - ey
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.001)
            step_x = (dx / dist) * self.speed
            step_y = (dy / dist) * self.speed

            # --- Test collisions map ---
            new_x = ex + step_x
            new_y = ey + step_y + enemy['vy']

            if not self.tilemap.solid_check((new_x, ey)):
                enemy['x'] = new_x
            else:
                enemy['x'] = ex - step_x * 0.5

            if not self.tilemap.solid_check((enemy['x'], new_y)):
                enemy['y'] = new_y
            else:
                enemy['vy'] = 0

            # Limites de la map
            enemy['x'] = max(0, min(enemy['x'], 1000))
            enemy['y'] = max(0, min(enemy['y'], 1000))
