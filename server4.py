import socket
import struct
import time
import random
import miniupnpc

# --- Configuration du serveur ---
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5005
UPDATE_RATE = 1 / 30

# --- UPnP : ouvrir le port sur le routeur ---
upnp = miniupnpc.UPnP()
upnp.discoverdelay = 200
print("Recherche du routeur UPnP...")
upnp.discover()
upnp.selectigd()

try:
    upnp.addportmapping(SERVER_PORT, 'UDP', upnp.lanaddr, SERVER_PORT, 'Python Game Server', '')
    print(f"Port {SERVER_PORT} ouvert via UPnP !")
    print(f"IP publique : {upnp.externalipaddress()}")
except Exception as e:
    print("Impossible d'ouvrir le port via UPnP :", e)

# --- Serveur UDP ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))
print(f"Server running on {SERVER_IP}:{SERVER_PORT}")

clients = {}   # addr -> id
players = {}   # id -> (x, y, vx, vy)
enemies = {}    # enemy_id -> {'x': float, 'y': float, 'target_player': int or None}
next_id = 1
next_enemy_id = 1
last_update = time.time()
ENEMY_SPEED = 0.5  # Vitesse des ennemis
ENEMIES_PER_PLAYER = 2  # Nombre d'ennemis par joueur

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if not data:
                continue
 
            msg_type = data[0]

            # --- Nouveau joueur ---
            if addr not in clients and msg_type == 0:
                clients[addr] = next_id
                players[next_id] = (0, 0, 0, 0)
                print(f"New player {next_id} connected {addr}")
                
                # Créer des ennemis près du nouveau joueur
                px, py = players[next_id][0], players[next_id][1]
                for i in range(ENEMIES_PER_PLAYER):
                    enemy_id = next_enemy_id
                    # Position aléatoire près du joueur (dans un rayon de 100-200 pixels)
                    angle = random.random() * 2 * 3.14159
                    distance = 100 + random.random() * 100
                    enemy_x = px + distance * (random.random() - 0.5)
                    enemy_y = py + distance * (random.random() - 0.5)
                    enemies[enemy_id] = {
                        'x': enemy_x,
                        'y': enemy_y,
                        'target_player': next_id
                    }
                    next_enemy_id += 1
                    print(f"Created enemy {enemy_id} at ({enemy_x:.1f}, {enemy_y:.1f}) for player {next_id}")
                
                # Envoyer seulement l'ID (plus besoin de is_host)
                sock.sendto(struct.pack("I", next_id), addr)
                next_id += 1

            # --- Déconnexion ---
            elif msg_type == 1:
                if addr in clients:
                    pid = clients[addr]
                    print(f"Player {pid} disconnected {addr}")
                    del players[pid]
                    del clients[addr]
                    # Réassigner les ennemis ciblant ce joueur ou les supprimer
                    enemies_to_remove = []
                    for eid, enemy in enemies.items():
                        if enemy.get('target_player') == pid:
                            # Réassigner à un autre joueur ou supprimer
                            if players:
                                # Trouver le joueur le plus proche
                                ex, ey = enemy['x'], enemy['y']
                                closest_player = None
                                closest_dist = float('inf')
                                for other_pid, (px, py, _, _) in players.items():
                                    dist = ((px - ex)**2 + (py - ey)**2)**0.5
                                    if dist < closest_dist:
                                        closest_dist = dist
                                        closest_player = other_pid
                                enemy['target_player'] = closest_player
                            else:
                                # Plus de joueurs, marquer pour suppression
                                enemies_to_remove.append(eid)
                    # Supprimer les ennemis marqués
                    for eid in enemies_to_remove:
                        del enemies[eid]
                continue

            # --- Update position joueur ---
            if msg_type == 0 and addr in clients:
                pid = clients[addr]
                if len(data) >= 17:
                    x, y, vx, vy = struct.unpack("ffff", data[1:17])
                    players[pid] = (x, y, vx, vy)
            
            # --- Envoi des mises à jour ---
            now = time.time()
            if now - last_update >= UPDATE_RATE:
                last_update = now
                
                # --- Calculer le déplacement des ennemis vers le joueur le plus proche ---
                for eid, enemy in enemies.items():
                    target_player = enemy.get('target_player')
                    if target_player and target_player in players:
                        px, py, _, _ = players[target_player]
                        ex, ey = enemy['x'], enemy['y']
                        
                        # Calculer la direction vers le joueur
                        dx = px - ex
                        dy = py - ey
                        dist = (dx**2 + dy**2)**0.5
                        
                        if dist > 5:  # Se déplacer si on n'est pas déjà très proche
                            # Normaliser et multiplier par la vitesse
                            dx_norm = (dx / dist) * ENEMY_SPEED if dist > 0 else 0
                            dy_norm = (dy / dist) * ENEMY_SPEED if dist > 0 else 0
                            
                            enemy['x'] += dx_norm
                            enemy['y'] += dy_norm
                        # Si le joueur cible n'existe plus, trouver un nouveau cible
                    elif target_player is None or target_player not in players:
                        # Trouver le joueur le plus proche
                        if players:
                            ex, ey = enemy['x'], enemy['y']
                            closest_player = None
                            closest_dist = float('inf')
                            for pid, (px, py, _, _) in players.items():
                                dist = ((px - ex)**2 + (py - ey)**2)**0.5
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_player = pid
                            enemy['target_player'] = closest_player
                
                # Payload: [nb_players: B] [players...] [nb_enemies: B] [enemies...]
                payload = struct.pack("B", len(players))
                for pid, (px, py, pvx, pvy) in players.items():
                    payload += struct.pack("Iffff", pid, px, py, pvx, pvy)
                # Ajouter les ennemis (format simplifié: juste x, y)
                payload += struct.pack("B", len(enemies))
                for eid, enemy in enemies.items():
                    payload += struct.pack("Iff", eid, enemy['x'], enemy['y'])
                for c in clients:
                    sock.sendto(payload, c)

        except Exception as e:
            # print("Error:", e)
            pass
except KeyboardInterrupt:
    print("Fermeture du serveur...")
    try:
        upnp.deleteportmapping(SERVER_PORT, 'UDP')
        print("Redirection UPnP supprimée.")
    except:
        pass
    sock.close()
