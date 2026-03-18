import pygame, random

# --- Initialisation ---
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music/sqz.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play()
pygame.mixer.music.play(loops=-1)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TP Noël - Attrape les cadeaux !")
clock = pygame.time.Clock()

# --- Chargement des images ---
background = pygame.image.load("images/fond_enneige.jpg")
heal = pygame.image.load("images/coeur.png").convert_alpha()
power_up = pygame.image.load("images/cadeau_bleu.png").convert_alpha()
gift = pygame.image.load("images/cadeau.png").convert_alpha()
snowball = pygame.image.load("images/boule_de_neige.png").convert_alpha()
perdu = pygame.image.load("images/gameover.png")

# Spritesheet du Père Noël (par ex. 4 frames de 64x64 pixels)
spritesheet = pygame.image.load("images/Sprites_Santa.png").convert_alpha()
spritesheet.set_colorkey((0,128,0))
size = spritesheet.get_size()
bigger_img = pygame.transform.scale(spritesheet, (int(size[0]*9), int(size[1]*9)))

def get_frame(sheet, x, y, width, height):
    """Extrait une frame du spritesheet"""
    frame = pygame.Surface((35, 35), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), (x, y, width, height))
    return frame

# Création des frames du Père Noël
frame_hauteur = 33
frame_longeur = 33
frames = [get_frame(spritesheet, i*frame_longeur, 0, frame_hauteur, frame_longeur) for i in range(4)]
frames_droite = [pygame.transform.flip(f, True, False) for f in frames]

# --- Variables de jeu ---
santa_x, santa_y = WIDTH // 2, HEIGHT - 100
current_frame = 0
frame_delay = 5
tick = 0
direction = 'immobile'
partie_terminee = False
snowball_collision_sound = pygame.mixer.Sound("music/sniperz.wav")
gameover = pygame.mixer.Sound("music/mario.wav")
gift_collision_sound = pygame.mixer.Sound("music/gifts.wav")
pygame.mixer.Sound.set_volume(gift_collision_sound, 0.2)
cadeau_bleu_sound = pygame.mixer.Sound("music/cadeaubleu.wav")
pygame.mixer.Sound.set_volume(cadeau_bleu_sound, 1)
heal_sound = pygame.mixer.Sound("music/heal.wav")
pygame.mixer.Sound.set_volume(heal_sound, 1)


score = 0
lives = 3
gifts = []
powers_up = []
snowballs = []
heals = []

# --- Boucle principale ---
running = True
while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Déplacement du Père Noël
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and santa_x > 0:  
        santa_x -= 5  
        direction = 'gauche'
    elif keys[pygame.K_RIGHT] and santa_x < WIDTH - 64:  
        santa_x += 5 
        direction = 'droite'
    else:
        direction = 'immobile'
    
    #bordure de la map
    border_thickness = 10
    left_border = pygame.Rect(0, 0, border_thickness, HEIGHT)
    right_border = pygame.Rect(WIDTH - border_thickness, 0, border_thickness, HEIGHT)
    top_border = pygame.Rect(0, 0, WIDTH, border_thickness)
    bottom_border = pygame.Rect(0, HEIGHT - border_thickness, WIDTH, border_thickness)
    
    # Apparition aléatoire des objets
    if partie_terminee == False:
        if random.randint(1, 1000) == 1:
            heals.append([random.randint(0, WIDTH - power_up.get_width()), 0])
        if random.randint(1, 500) == 1:
            powers_up.append([random.randint(0, WIDTH - power_up.get_width()), 0])
        if random.randint(1, 45) == 1:
            gifts.append([random.randint(0, WIDTH - gift.get_width()), 0])
        if random.randint(1, 8) == 1:
            snowballs.append([random.randint(0, WIDTH - snowball.get_width()), 0])

    # Mise à jour des cadeaux
    for g in gifts[:]:
        g[1] += 5
        screen.blit(gift, g)
        if abs(g[0] - santa_x) < 40 and abs(g[1] - santa_y) < 40:
            score += 1
            gifts.remove(g)
            gift_collision_sound.play()
            if keys[pygame.K_LEFT] and santa_x > 0:  
                santa_x -= 5  
                direction = 'gauche'
            elif keys[pygame.K_RIGHT] and santa_x < WIDTH - 64:  
                santa_x += 5 
                direction = 'droite'
            else:
                direction = 'immobile'
    
    # Mise à jour des powers up
    for p in powers_up[:]:
        p[1] += 5
        screen.blit(power_up, p)
        if abs(p[0] - santa_x) < 40 and abs(p[1] - santa_y) < 40:
            score += 3
            powers_up.remove(p)
            cadeau_bleu_sound.play()
            
    # Mise à jour des heal
    for h in heals[:]:
        h[1] += 5
        screen.blit(heal, h)
        if abs(h[0] - santa_x) < 40 and abs(h[1] - santa_y) < 40:
            lives += 1
            heals.remove(h)
            heal_sound.play()
           
    # Mise à jour des boules de neige
    for s in snowballs[:]:
        s[1] += 11
        screen.blit(snowball, s)
        if abs(s[0] - santa_x) < 40 and abs(s[1] - santa_y) < 40:
            lives -= 1
            snowball_collision_sound.play()
            snowballs.remove(s)

    # Animation du Père Noël
    tick +=1
    if tick % frame_delay == 0:
            current_frame = (current_frame + 1) % len(frames)
    if direction == 'gauche':
        screen.blit(pygame.transform.scale(frames_droite[current_frame],(60,60)), (santa_x, santa_y))
    elif direction == 'droite':
        screen.blit(pygame.transform.scale(frames[current_frame],(60,60)), (santa_x, santa_y))
    elif direction == 'immobile':
        screen.blit(pygame.transform.scale(frames[0],(60,60)), (santa_x, santa_y))

    # Affichage du score et des vies
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score : {score}   Vies : {lives}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    if lives <= 0 :
        screen.blit(perdu, (0, 0))
        partie_terminee = True
        gameover.play()
        pygame.mixer.music.stop()
        
        
    pygame.display.flip()
    clock.tick(30)
  
pygame.quit()
