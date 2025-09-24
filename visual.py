import pygame
import sys
import networkx as nx
from fourmi import Fourmiliere
from main import charger_fichier
import math
import time


# ================
# Initialisation pygame
# ================
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation graphique - Fourmilière")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

background = pygame.image.load("images/terre.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

fourmi_img = pygame.image.load("images/fourmi.png")
fourmi_img = pygame.transform.scale(fourmi_img, (20, 20))  # taille adaptée

# ================
# Fonction de dessin
# ================
def draw_fourmiliere(fourmiliere, pos, fourmis_pos):
    
    screen.blit(background, (0, 0))

    # dessiner tunnels
    for s1, voisins in fourmiliere.tunnels.items():
        for s2 in voisins:
            pygame.draw.line(screen, (101, 67, 33), pos[s1], pos[s2], 25)  # marron sombre

    # dessiner salles
    for nom, salle in fourmiliere.salles.items():
        pygame.draw.circle(screen, (205, 133, 63), pos[nom], 30)   # salle claire
        pygame.draw.circle(screen, (139, 69, 19), pos[nom], 30, 3) # contour sombre
        img = font.render(nom, True, (255, 255, 255))
        rect = img.get_rect(center=pos[nom])
        screen.blit(img, rect)

    # dessiner fourmis
    for f_id, (x, y) in fourmis_pos.items():
        rect = fourmi_img.get_rect(center=(int(x), int(y)))
        screen.blit(fourmi_img, rect)

    pygame.display.flip()


def interpolate(p1, p2, t):
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)


# ================
# Fonction principale
# ================
def visualiser(fourmiliere, logs):
    # layout automatique des salles avec networkx
    G = fourmiliere.construire_graphe()
    layout = nx.spring_layout(G, scale=300, center=(WIDTH//2, HEIGHT//2))

    # positions des salles dans pygame (int arrondis)
    pos = {salle: (int(x), int(y)) for salle, (x, y) in layout.items()}

    # positions actuelles des fourmis (au départ dans Sv)
    fourmis_pos = {f.id: pos["Sv"] for f in fourmiliere.fourmis}

    for step in logs:
        lignes = step.splitlines()[1:]  # ignorer "+++ E1 +++"
        mouvements = []
        for l in lignes:
            # ex: "f1 - S1 - S2"
            fid, dep, arr = [x.strip() for x in l.split("-")]
            fid = int(fid[1:])  # "f1" -> 1
            mouvements.append((fid, dep, arr))

        # animer les déplacements
        for t in [i/30 for i in range(31)]:  # 30 frames pour la transition
            for fid, dep, arr in mouvements:
                start = pos[dep]
                end = pos[arr]
                fourmis_pos[fid] = interpolate(start, end, t)

            draw_fourmiliere(fourmiliere, pos, fourmis_pos)
            clock.tick(30)

    # attendre un peu à la fin
    time.sleep(3)


# ================
# Point d'entrée
# ================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visual.py <fichier_fourmiliere.txt>")
        sys.exit(1)

    path = sys.argv[1]
    fourmiliere = charger_fichier(path)
    logs = fourmiliere.simuler()

    visualiser(fourmiliere, logs)

    pygame.quit()
