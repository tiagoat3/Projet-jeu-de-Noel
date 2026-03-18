import pygame
import sys
import random
from config import *

pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Casse-Brique")
clock = pygame.time.Clock()

police = pygame.font.SysFont(None, 48)

pygame.mixer.init()
pygame.mixer.music.load("music/theme.mp3")
brique_cassee = pygame.mixer.Sound("music/huh.wav")
lose = pygame.mixer.Sound("music/lose.wav")
win = pygame.mixer.Sound("music/win.wav")
raquette_collision = pygame.mixer.Sound("music/boum.wav")

ecran_titre = pygame.image.load("image/ecran_titre.jpg")
fond = pygame.image.load("image/fond.png")
ecran_lose = pygame.image.load("image/ecran_lose.jpg")
ecran_win = pygame.image.load("image/ecran_win.jpg")

class Balle:
    def __init__(self):
        
        self.abscisse = 370
        self.ordonnee = 880
        self.couleur = NOIR
        self.vitesse_x = BAL_VITESSE
        self.vitesse_y = BAL_VITESSE
        self.rayon = BAL_RADIUS
        self.score = 0
        self.image = pygame.image.load("image/balle.png")
        self.rect = pygame.Rect(self.abscisse, self.ordonnee, self.image.get_width(), self.image.get_height())
    
    def draw(self, fenetre):
        fenetre.blit(self.image, (self.abscisse, self.ordonnee))
        
    def move(self):
        self.abscisse += self.vitesse_x     # Incrémente les abscisses avec la vitesse
        self.ordonnee += self.vitesse_y     # Incrémente les abscisses avec la vitesse
        
        # Met à jour la boite de collision de la balle quand elle bouge
        self.rect.x = self.abscisse     
        self.rect.y = self.ordonnee
        
    def collision_mur(self):
        if self.abscisse + self.rayon > LARGEUR or self.abscisse < 0:
            self.vitesse_x = -self.vitesse_x
    
        if self.ordonnee + self.rayon > HAUTEUR or self.ordonnee < 0:
            self.vitesse_y = -self.vitesse_y
    
    def collision_brique(self, brique):
        if self.rect.colliderect(brique.rect):
    
            # Calcul du chevauchement
            face_gauche = self.rect.right - brique.rect.left
            face_droite = brique.rect.right - self.rect.left
            face_haut = self.rect.bottom - brique.rect.top
            face_bas = brique.rect.bottom - self.rect.top
    
            face = min(face_gauche, face_droite, face_haut, face_bas)
    
            # Collision horizontale
            if face == face_gauche or face == face_droite:
                self.vitesse_x = -self.vitesse_x    # Inverse la vitesse
    
            # Collision verticale
            else:
                self.vitesse_y = -self.vitesse_y    # Inverse la vitesse
    
            # Sort la balle de la brique
            self.rect.x += self.vitesse_x
            self.rect.y += self.vitesse_y
            self.abscisse = self.rect.x
            self.ordonnee = self.rect.y
    
            brique.vie -= 1
            self.score += 10
            brique_cassee.play()    # Lance le son de collision


class Brique:
    def __init__(self, x, y):
        
        self.position = [x, y]
        self.largeur = BRIQUE_LARGEUR
        self.hauteur = BRIQUE_HAUTEUR
        self.vie = 1
        self.image = pygame.image.load("image/brique.png")
        self.rect = pygame.Rect(self.position[0], self.position[1], self.image.get_width(), self.image.get_height())
        
    def draw(self, fenetre):
        if self.vie == 1:
            fenetre.blit(self.image, self.position)
        
class Raquette:
    def __init__(self, x, y):
        
        self.position = [x, y]
        self.vitesse = RAQUETTE_VITESSE
        self.largeur = RAQUETTE_LARGEUR
        self.hauteur = RAQUETTE_HAUTEUR
        self.image = pygame.image.load("image/raquette.png")
        self.rect = pygame.Rect(x, y, self.largeur, self.hauteur)
        
    def collision_mur(self):
        if self.position[0] + self.largeur >= LARGEUR :
            self.position[0] = LARGEUR - RAQUETTE_LARGEUR   #collision droite
            
        if self.position[0] <= 0:
            self.position[0] = 0   # collision gauche
            
        
    def collision_balle(self, balle):
        if balle.rect.colliderect(self.rect):
            balle.vitesse_y = -abs(balle.vitesse_y)
            raquette_collision.play()
    
    def move(self, touches):
        if touches == "LEFT":
            self.position[0] -= self.vitesse
    
        if touches == "RIGHT":
            self.position[0] += self.vitesse
    
        self.rect.x = self.position[0]  # Met à jour la boite de collision de la raquette quand elle bouge
    
    def draw(self, fenetre):
        fenetre.blit(self.image, self.position)
  
def afficher_ecran_titre(fenetre, police, ecran_titre):
    """
    Fonction pour afficher l'écran titre lorsque la touche entrée du clavier
    est pressée.
    """
    
    fenetre.blit(ecran_titre, (0,0))    # Affiche l'image de l'écran titre

    message = police.render("Appuyez sur entrée !", True, BLANC)
    fenetre.blit(message, (LARGEUR//2 - 150, HAUTEUR//2))   # Affiche le message de début de jeu

    pygame.display.flip()

def gestion_jeu(balle, raquette, briques):
    """
    Fonction pour gérer le fonctionnement du jeu : le mouvement de la balle,
    les collisions entre la balle et la raquette, la raquette et les murs, la balle
    et les murs et entre la balle et les briques et la suppression
    des briques de la liste de briques.
    """
    
    balle.move()    # Bouge la balle
    
    raquette.collision_mur()    # Gère les collisions raquette/mur
    balle.collision_mur()   # Gère les collisions balle/mur

    raquette.collision_balle(balle) # Gère les collisions raquette/balle

    for i in range(len(briques)-1, -1, -1):     # Supprime les briques de la liste
        balle.collision_brique(briques[i])
        if briques[i].vie == 0:
            briques.pop(i)
            
def afficher_jeu(fenetre, balle, raquette, briques, police):
    """
    Fonction pour afficher tous les éléments du jeu : remplir le fond en gris,
    dessiner la raquette, la balle et les briques et afficher et incrémenter le
    score.
    """
    
    fenetre.blit(fond, (0,0))  # Met une image de fond

    raquette.draw(fenetre)  # Dessine la raquette
    balle.draw(fenetre) # Dessine la balle

    for brique in briques:
        brique.draw(fenetre) # Dessine les briques

    score = police.render(f"Score : {balle.score}", True, NOIR) # Affiche le score
    fenetre.blit(score, (10,10))

    pygame.display.flip()
    
def defaite(balle, lose, police, fenetre, ecran_lose):
    """
    Fonction qui gère la condition de défaite et stop le jeu en cas de défaite
    """

    pygame.mixer.music.stop()   # Stop la musique de fond
    lose.play()     # Lance le son de défaite
    
    fenetre.blit(ecran_lose, (0,0))    # Affiche l'image de l'écran de fin
    
    message = police.render("Vous avez perdu !", True, NOIR)
    fenetre.blit(message, (LARGEUR//2 - 150, HAUTEUR//2)) # Affiche message de 
    
    message = police.render("Appuyez sur R pour relancer !", True, VIOLET)
    fenetre.blit(message, (LARGEUR//6, HAUTEUR//4)) # Affiche message de pour relancer
    
    message = police.render(f"Vous avez fait {balle.score} points !", True, CYAN)
    fenetre.blit(message, (LARGEUR//4, HAUTEUR//2.8)) # Affiche score de fin
    
    pygame.display.flip()


def victoire(briques, police, fenetre, ecran_win):
    """
    Fonction qui gère la condition de victoire et stop le jeu en cas de victoire
    """
    
    pygame.mixer.music.stop()   # Stop la musique de fond
    win.play()     # Lance le son de victoire
    
    fenetre.blit(ecran_win, (0,0))    # Affiche l'image de l'écran de fin
    
    message = police.render("Vous avez gagné !", True, NOIR)
    fenetre.blit(message, (LARGEUR//2 - 150, HAUTEUR//2)) # Affiche message de fin
    
    message = police.render("Appuyez sur R pour relancer !", True, VIOLET)
    fenetre.blit(message, (LARGEUR//6, HAUTEUR//4)) # Affiche message de pour relancer
    
    message = police.render(f"Vous avez fait {balle.score} points !", True, CYAN)
    fenetre.blit(message, (LARGEUR//4, HAUTEUR//2.8)) # Affiche score de fin
    
    pygame.display.flip()

def redemarrer_jeu():
    """
    Fonction qui relance le jeu une fois que la touche r est préssée
    """
    
    global balle, raquette, briques, partie_terminee, fenetre, police
    
    # Recréer les objets
    balle = Balle()
    raquette = Raquette(350, 900)

    briques = [Brique(25, 50), Brique(75, 50), Brique(125, 50), Brique(175, 50), Brique(225, 50), Brique(275, 50), Brique(325, 50), Brique(375,50), Brique(425,50), Brique(475, 50), Brique(525, 50),Brique(575, 50), Brique(625, 50),Brique(675, 50),Brique(725, 50),
               Brique(200, 110), Brique(200, 135), Brique(200, 160), Brique(200, 185), Brique(200, 210), Brique(200, 235), Brique(200, 260), Brique(200, 285), Brique(200, 310), Brique(200, 335), Brique(200, 360), Brique(200, 385), Brique(200, 410), Brique(200, 435), Brique(200, 460), Brique(200, 485),
               Brique(250, 110), Brique(250, 135), Brique(250, 160), Brique(250, 185), Brique(250, 210), Brique(250, 235), Brique(250, 260), Brique(250, 285), Brique(250, 310), Brique(250, 335), Brique(250, 360), Brique(250, 385), Brique(250, 410), Brique(250, 435), Brique(250, 460), Brique(250, 485),
               Brique(300, 110), Brique(350, 110), Brique(400, 110), Brique(450, 110), Brique(500, 110),
               Brique(300, 135), Brique(350, 135), Brique(400, 135), Brique(450, 135), Brique(500, 135),
               Brique(475, 160), Brique(525, 160), Brique(475, 185), Brique(525, 185), Brique(475, 210), Brique(525, 210), Brique(475, 235), Brique(525, 235), Brique(475, 260), Brique(525, 260),
               Brique(450, 285), Brique(500, 285), Brique(400, 285), Brique(350, 285), Brique(300, 285),
               Brique(450, 310), Brique(500, 310), Brique(400, 310), Brique(350, 310), Brique(300, 310),
               Brique(475, 335), Brique(525, 335), Brique(475, 360), Brique(525, 360), Brique(475, 385), Brique(525, 385), Brique(475, 410), Brique(525, 410), Brique(475, 435), Brique(525, 435),          
               Brique(300, 460), Brique(350, 460), Brique(400, 460), Brique(450, 460), Brique(500, 460),
               Brique(300, 485), Brique(350, 485), Brique(400, 485), Brique(450, 485), Brique(500, 485),
               Brique(25, 550), Brique(75, 550), Brique(125, 550), Brique(175, 550), Brique(225, 550), Brique(275, 550), Brique(325, 550), Brique(375,550), Brique(425,550), Brique(475, 550), Brique(525, 550),Brique(575, 550), Brique(625, 550),Brique(675, 550),Brique(725, 550),
               ]

    # Relancer la musique
    pygame.mixer.music.play(loops=-1)

    # Relancer la partie
    partie_terminee = False
 
raquette = Raquette(350, 900)
briques = [Brique(25, 50), Brique(75, 50), Brique(125, 50), Brique(175, 50), Brique(225, 50), Brique(275, 50), Brique(325, 50), Brique(375,50), Brique(425,50), Brique(475, 50), Brique(525, 50),Brique(575, 50), Brique(625, 50),Brique(675, 50),Brique(725, 50),
           Brique(200, 110), Brique(200, 135), Brique(200, 160), Brique(200, 185), Brique(200, 210), Brique(200, 235), Brique(200, 260), Brique(200, 285), Brique(200, 310), Brique(200, 335), Brique(200, 360), Brique(200, 385), Brique(200, 410), Brique(200, 435), Brique(200, 460), Brique(200, 485),
           Brique(250, 110), Brique(250, 135), Brique(250, 160), Brique(250, 185), Brique(250, 210), Brique(250, 235), Brique(250, 260), Brique(250, 285), Brique(250, 310), Brique(250, 335), Brique(250, 360), Brique(250, 385), Brique(250, 410), Brique(250, 435), Brique(250, 460), Brique(250, 485),
           Brique(300, 110), Brique(350, 110), Brique(400, 110), Brique(450, 110), Brique(500, 110),
           Brique(300, 135), Brique(350, 135), Brique(400, 135), Brique(450, 135), Brique(500, 135),
           Brique(475, 160), Brique(525, 160), Brique(475, 185), Brique(525, 185), Brique(475, 210), Brique(525, 210), Brique(475, 235), Brique(525, 235), Brique(475, 260), Brique(525, 260),
           Brique(450, 285), Brique(500, 285), Brique(400, 285), Brique(350, 285), Brique(300, 285),
           Brique(450, 310), Brique(500, 310), Brique(400, 310), Brique(350, 310), Brique(300, 310),
           Brique(475, 335), Brique(525, 335), Brique(475, 360), Brique(525, 360), Brique(475, 385), Brique(525, 385), Brique(475, 410), Brique(525, 410), Brique(475, 435), Brique(525, 435),          
           Brique(300, 460), Brique(350, 460), Brique(400, 460), Brique(450, 460), Brique(500, 460),
           Brique(300, 485), Brique(350, 485), Brique(400, 485), Brique(450, 485), Brique(500, 485),
           Brique(25, 550), Brique(75, 550), Brique(125, 550), Brique(175, 550), Brique(225, 550), Brique(275, 550), Brique(325, 550), Brique(375,550), Brique(425,550), Brique(475, 550), Brique(525, 550),Brique(575, 550), Brique(625, 550),Brique(675, 550),Brique(725, 550),
           ]
balle = Balle()

lancement_partie = False
partie_terminee = True
running = True

while running:
    clock.tick(FPS)
    
    if not lancement_partie:
        afficher_ecran_titre(fenetre, police, ecran_titre)
        
        # Lancer la partie
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    lancement_partie = True
                    partie_terminee = False
                    pygame.mixer.music.play(loops=-1)
        
    for event in pygame.event.get():
        # Quitter le jeu
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            
        # Relancer le jeu
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if partie_terminee:
                        redemarrer_jeu()
    
    else:       # Gère les déplacements de la raquette quand les touches sont préssées
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  # Déplacement vers la gauche
                raquette.move("LEFT")
                        
            if event.key == pygame.K_RIGHT: # Déplacement vers la droite
                raquette.move("RIGHT")
        
    if not partie_terminee:
        gestion_jeu(balle, raquette, briques)
        afficher_jeu(fenetre, balle, raquette, briques, police)
        
        if balle.ordonnee + balle.rayon >= HAUTEUR: # Condition de défaite
            defaite(balle, lose, police, fenetre, ecran_lose)
            partie_terminee = True
        
        if len(briques) == 0:   # Condition de victoire
        
            victoire(briques, police, fenetre, ecran_win)
            partie_terminee = True
