import pygame
import sys
from pygame import mixer
import random
import math

# Initialisation de Pygame
pygame.init()

# Configuration de l'écran
taille_ecran = (800, 600)
ecran = pygame.display.set_mode(taille_ecran)

# Charger et configurer les polices de caractères
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 30)

# Chargement des sprites
vaisseau = pygame.image.load('vaisseau.png')
mechant1 = pygame.image.load('mechant1.png')
mechant2 = pygame.image.load('mechant2.png')
mechant3 = pygame.image.load('mechant3.png')
explosion = pygame.image.load('explo.png')
fond = pygame.image.load('space.jpg')

# Charger les sons
mixer.music.load('musique.mp3')
mixer.music.play(-1)
son_tir = mixer.Sound('tir.wav')

# Initialisation du vaisseau et des vies
vaisseau_pos = [350, 500]
vies = 5
vaisseau_miniature = pygame.transform.scale(vaisseau, (20, 20))  # Création d'une version miniature du vaisseau pour l'affichage des vies

# Initialisation des méchants
def init_mechants(niveau):
    mechants = []
    if niveau == 1:
        for i in range(4):
            for j in range(10):
                mechant = random.choice([mechant1, mechant2, mechant3])
                mechants.append({'sprite': mechant, 'pos': [50 + j * 70, 50 + i * 70], 'dir': 1})
    elif niveau == 2:
        for i in range(7):
            for j in range(i+1):
                mechant = random.choice([mechant1, mechant2, mechant3])
                mechants.append({'sprite': mechant, 'pos': [370 - j * 35 + i * 35, 50 + i * 50], 'dir': 1})
    elif niveau == 3:
        # Disposition en cercle
        for i in range(20):
            angle = i * 2 * math.pi / 20
            x = int(400 + 200 * math.cos(angle))
            y = int(200 + 200 * math.sin(angle))
            mechant = random.choice([mechant1, mechant2, mechant3])
            mechants.append({'sprite': mechant, 'pos': [x, y], 'dir': 1})
    elif niveau == 4:
        # Disposition en spirale
        for i in range(30):
            angle = i * 12 * 2 * math.pi / 30
            radius = i * 10
            x = int(400 + radius * math.cos(angle))
            y = int(200 + radius * math.sin(angle))
            mechant = random.choice([mechant1, mechant2, mechant3])
            mechants.append({'sprite': mechant, 'pos': [x, y], 'dir': 1})

    return mechants

# Initialisation du jeu
def init_jeu():
    global niveau, mechants, tirs, tirs_mechants, explosions, show_niveau, niveau_timer, vies, vaisseau_pos
    niveau = 1
    mechants = init_mechants(niveau)
    tirs = []
    tirs_mechants = []
    explosions = []
    show_niveau = True
    niveau_timer = pygame.time.get_ticks()
    vies = 5
    vaisseau_pos = [350, 500]

# Initialisation du niveau
init_jeu()

# Initialisation du fond
scroll_y = 0

# Boucle principale du jeu
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tirs.append([vaisseau_pos[0]+16, vaisseau_pos[1]])
                son_tir.play()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        vaisseau_pos[0] -= 5
    if keys[pygame.K_RIGHT]:
        vaisseau_pos[0] += 5

    ecran.fill((0, 0, 0))

    # Affichage des vies
    for i in range(vies):
        ecran.blit(vaisseau_miniature, (10 + i * 30, 10))

    # Scroll du fond
    rel_y = scroll_y % fond.get_rect().height
    ecran.blit(fond, (0, rel_y - fond.get_rect().height))
    if rel_y < taille_ecran[1]:
        ecran.blit(fond, (0, rel_y))
    scroll_y += 1

    # Affichage du niveau
    if show_niveau:
        niveau_surface = myfont.render('NIVEAU ' + str(niveau), False, (255, 255, 255))
        ecran.blit(niveau_surface, (350, 300))
        if pygame.time.get_ticks() - niveau_timer > 2000:
            show_niveau = False

    for tir in tirs:
        pygame.draw.rect(ecran, (255, 255, 255), pygame.Rect(tir[0], tir[1], 2, 10))
        tir[1] -= 5

    for tir in tirs_mechants:
        pygame.draw.rect(ecran, (255, 0, 0), pygame.Rect(tir[0], tir[1], 2, 10))
        tir[1] += 5
        if vaisseau_pos[0] < tir[0] < vaisseau_pos[0] + 50 and vaisseau_pos[1] < tir[1] < vaisseau_pos[1] + 50:
            tirs_mechants.remove(tir)
            explosions.append([explosion, vaisseau_pos.copy(), pygame.time.get_ticks()])
            vies -= 1  # Diminution des vies
            if vies == 0:  # Game Over
                game_over_surface = myfont.render('GAME OVER', False, (255, 0, 0))
                ecran.blit(game_over_surface, (350, 300))
                pygame.display.flip()
                pygame.time.wait(2000)
                init_jeu()
            else:  # Réinitialisation de la position du vaisseau
                vaisseau_pos = [350, 500]

    for mechant in mechants[:]:
        mechant['pos'][0] += mechant['dir']
        if mechant['pos'][0] < 10 or mechant['pos'][0] > 730:
            mechant['dir'] *= -1
            mechant['pos'][1] += 10
        if random.randint(0, 1000) < 1:  # réduire le taux de tir des méchants
            tirs_mechants.append([mechant['pos'][0], mechant['pos'][1]])
        for tir in tirs[:]:
            if tir[0] > mechant['pos'][0] and tir[0] < mechant['pos'][0] + 32 and tir[1] > mechant['pos'][1] and tir[1] < mechant['pos'][1] + 32:
                tirs.remove(tir)
                mechants.remove(mechant)
                explosions.append([explosion, mechant['pos'].copy(), pygame.time.get_ticks()])
                if not mechants:  # tous les méchants sont morts
                    niveau += 1
                    mechants = init_mechants(niveau)
                    show_niveau = True
                    niveau_timer = pygame.time.get_ticks()
        else:
            ecran.blit(mechant['sprite'], mechant['pos'])

    for expl in explosions[:]:
        if pygame.time.get_ticks() - expl[2] > 200:
            explosions.remove(expl)
        else:
            ecran.blit(expl[0], expl[1])

    ecran.blit(vaisseau, vaisseau_pos)
    pygame.display.flip()

    pygame.time.delay(10)