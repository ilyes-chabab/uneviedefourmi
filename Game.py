import pygame, sys, os, time
from main import charger_fichier

pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation graphique - Fourmilière")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 32)

# Background
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((50, 50, 50))

# Dossier contenant les fichiers
FOLDER = "four"
files = [f for f in os.listdir(FOLDER) if f.endswith(".txt")]

# Boutons pour sélectionner les fichiers
button_width, button_height = 200, 40
buttons = []
for i, f in enumerate(files):
    rect = pygame.Rect(20, 20 + i*(button_height+10), button_width, button_height)
    buttons.append((rect, f))

# Image de fourmi
fourmi_img = pygame.image.load("images/fourmi.png")
fourmi_img = pygame.transform.scale(fourmi_img, (20, 20))

# Animation helpers
def draw_buttons(selected=None):
    screen.fill((50, 50, 50))
    for rect, f in buttons:
        color = (200, 0, 0) if selected == f else (100, 100, 100)
        pygame.draw.rect(screen, color, rect)
        txt = font.render(f, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect.center)
        screen.blit(txt, txt_rect)

def interpolate(p1, p2, t):
    return (p1[0] + (p2[0]-p1[0])*t, p1[1] + (p2[1]-p1[1])*t)

def draw_simulation(fourmiliere, pos, fourmis_pos, logs, step_idx):
    # Partie gauche pour animation
    pygame.draw.rect(screen, (0, 0, 0), (0,0,WIDTH//2, HEIGHT))
    
    # Dessiner tunnels
    for s1, voisins in fourmiliere.tunnels.items():
        for s2 in voisins:
            pygame.draw.line(screen, (101,67,33), pos[s1], pos[s2], 25)
    # Dessiner salles
    for nom, salle in fourmiliere.salles.items():
        pygame.draw.circle(screen, (205,133,63), pos[nom], 30)
        pygame.draw.circle(screen, (139,69,19), pos[nom], 30, 3)
        img = font.render(nom, True, (255,255,255))
        rect = img.get_rect(center=pos[nom])
        screen.blit(img, rect)
    # Dessiner fourmis
    for f_id, (x,y) in fourmis_pos.items():
        rect = fourmi_img.get_rect(center=(int(x),int(y)))
        screen.blit(fourmi_img, rect)
    
    # Partie droite pour log
    pygame.draw.rect(screen, (30,30,30), (WIDTH//2,0,WIDTH//2, HEIGHT))
    y = 20
    for l in logs[max(0,step_idx-20):step_idx]:  # afficher les 20 dernières étapes
        for line in l.splitlines():
            txt = font.render(line, True, (255,255,255))
            screen.blit(txt, (WIDTH//2 + 20, y))
            y += 20

    pygame.display.flip()

def run_simulation(file_path):
    fourmiliere = charger_fichier(os.path.join(FOLDER, file_path))
    logs = fourmiliere.simuler()

    # layout automatique avec networkx
    import networkx as nx
    G = fourmiliere.construire_graphe()
    layout = nx.spring_layout(G, scale=300, center=(WIDTH//4, HEIGHT//2))
    pos = {salle: (int(x), int(y)) for salle, (x,y) in layout.items()}

    fourmis_pos = {f.id: pos["Sv"] for f in fourmiliere.fourmis}

    step_idx = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if step_idx < len(logs):
            lignes = logs[step_idx].splitlines()[1:]
            mouvements = []
            for l in lignes:
                fid, dep, arr = [x.strip() for x in l.split("-")]
                fid = int(fid[1:])
                mouvements.append((fid, dep, arr))
            
            for t in [i/30 for i in range(31)]:
                for fid, dep, arr in mouvements:
                    start = pos[dep]
                    end = pos[arr]
                    fourmis_pos[fid] = interpolate(start, end, t)
                draw_simulation(fourmiliere, pos, fourmis_pos, logs, step_idx)
                clock.tick(30)
            step_idx += 1
        else:
            # Fin de la simulation
            draw_simulation(fourmiliere, pos, fourmis_pos, logs, step_idx)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            time.sleep(0.1)

# ===== Main loop
selected_file = None
while True:
    draw_buttons(selected_file)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for rect, f in buttons:
                if rect.collidepoint(mx, my):
                    selected_file = f
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and selected_file:
                run_simulation(selected_file)
    clock.tick(30)
