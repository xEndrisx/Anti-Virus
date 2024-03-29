"""
 ________  ________   _________  ___  ___      ___ ___  ________  ___  ___  ________           ___      ___  _____
|\   __  \|\   ___  \|\___   ___\\  \|\  \    /  /|\  \|\   __  \|\  \|\  \|\   ____\         |\  \    /  /|/ __  \
\ \  \|\  \ \  \\ \  \|___ \  \_\ \  \ \  \  /  / | \  \ \  \|\  \ \  \\\  \ \  \___|_        \ \  \  /  / /\/_|\  \
 \ \   __  \ \  \\ \  \   \ \  \ \ \  \ \  \/  / / \ \  \ \   _  _\ \  \\\  \ \_____  \        \ \  \/  / /\|/ \ \  \
  \ \  \ \  \ \  \\ \  \   \ \  \ \ \  \ \    / /   \ \  \ \  \\  \\ \  \\\  \|____|\  \        \ \    / /      \ \  \
   \ \__\ \__\ \__\\ \__\   \ \__\ \ \__\ \__/ /     \ \__\ \__\\ _\\ \_______\____\_\  \        \ \__/ /        \ \__\
    \|__|\|__|\|__| \|__|    \|__|  \|__|\|__|/       \|__|\|__|\|__|\|_______|\_________\        \|__|/          \|__|
                                                                               \|_________|
"""
####################################################################
# Jeu AntiVirus | v1 [Fonctionnel] | Dev_Ils | Trophée de NSI 2024 #
####################################################################
#Python 3.x
#Pygame 2.5.2
####################################################################


import pygame
import sys
import os
from Classes import Piece, Piece_groupe, Bouton
from Fonctions import *

class AntiVirus:
    # Liste des coordonnées des segments formant les axes de déplacement du plateau
    axe_coord = [
        ((996, 100), (1194, 298)),
        ((798, 100), (1194, 496)),
        ((600, 100), (1194, 694)),
        ((600, 298), (996, 694)),
        ((600, 496), (798, 694)),
        ((798, 100), (600, 298)),
        ((996, 100), (600, 496)),
        ((1194, 100), (600, 694)),
        ((1194, 298), (798, 694)),
        ((1194, 496), (996, 694))
    ]

    def __init__(self, largeur, hauteur):
        # Initialisation de Pygame
        pygame.init()
        pygame.font.init()  # Initialisation du module de police

        # Initialisation de la fenêtre de jeu
        self.taille_fenetre = (largeur, hauteur)
        self.fenetre = pygame.display.set_mode(self.taille_fenetre)
        pygame.display.set_caption("Anti-Virus")

        # Initialisation de l'horloge pour le contrôle des images par seconde
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.fps_font = pygame.font.Font(None, 36)

        # Chemin vers la police
        chemin_police = "assets/Font/Zeniq_Nano.ttf"
        taille_police_niveau1 = 44
        taille_police_niveau2 = 30
        taille_police_niveau3 = 15

        # Chargement des polices
        self.police_niveau1 = pygame.font.Font(chemin_police, taille_police_niveau1)  # Niveau de titre 1
        self.police_niveau2 = pygame.font.Font(chemin_police, taille_police_niveau2)  # Niveau de titre 2
        self.police_niveau3 = pygame.font.Font(chemin_police, taille_police_niveau3)  # Niveau de titre 3
        self.textes = []
        self.textes_positions = []

        #Chargement des musiques et effets sonores

        # Charger la musique des menus principaux
        self.menu_music = pygame.mixer.Sound("sounds/musique_menus.mp3")
        self.level_music = pygame.mixer.Sound("sounds/musique_level.mp3")
        self.button1_sound = "sounds/button1.mp3"
        self.button2_sound = "sounds/button2.mp3"
        self.pieces1_sound = pygame.mixer.Sound("sounds/pieces1.mp3")

        self.menu_music.play(loops=-1)  # jouer la musique du menu en boucle
        self.current_music = self.menu_music  # Garder une trace de la musique actuellement jouée

        # Chargement des données du joueur
        self.game_data = lire_csv("game_data.csv")

        # Définition des groupes d'objets
        self.pieces = pygame.sprite.Group() #groupe des pièces du niveaux
        self.piece_en_deplacement = None #attribut de la pièce en déplacement
        self.pieces_deplacement = [] #attribut des pièces en déplacement en cas de déplacement groupé
        self.autoriser_deplacement = False #attribut autorisant ou non le déplacement des pièces
        self.old_x, self.old_y = None, None #attributs coordonnées initiales de la pièce en déplacement

        self.boutons = pygame.sprite.Group() #groupe des boutons de l'interface

        # État de l'interface utilisateur
        # 0 = niveau
        # 1 = main_menu
        # 2 = selection_difficulte_menu
        # 3 = selection_level_menu
        # 4 = victoire_menu
        self.etat_menu = 1
        self.main_menu()

        # charger en mémoire les images de l'animation du menu 2
        self.animation_images_SLM = self.charger_animation("assets/menus/selection_difficulte_menu/Animation/Débutant")
        self.animation_frame = 0 #initialisation
        self.animation_en_cours = False #attribut

    def charger_animation(self, dossier):
        # Charger les images d'une animation à partir d'un dossier
        images = []
        for fichier in sorted(os.listdir(dossier)):
            chemin = os.path.join(dossier, fichier)
            if os.path.isfile(chemin) and fichier.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = pygame.image.load(chemin).convert_alpha()
                images.append(image)
        return images

    def lancer_animations(self, liste_animation_images):
        # Afficher une séquence d'images pour une animation
        if self.animation_frame < len(liste_animation_images):
            self.fenetre.blit(liste_animation_images[self.animation_frame], (0, 0))
            self.animation_frame += 1
        else:
            # Réinitialiser l'animation à la fin
            self.animation_frame = 0
            self.animation_en_cours = False

    def dessiner_lignes(self, surface):
        # Dessiner les lignes délimitant les axes sur la surface spécifiée
        for coord in self.axe_coord:
            pygame.draw.aaline(surface, (255, 0, 0), coord[0], coord[1])

    def lancer_niveau(self, difficulte: str, niveau: int):
        # difficulté des niveaux : Explorer.exe Débutant, Kernel32 Avancé, Regedit Expert, System32 Maître
        # Mettre self.arriere_plan sur l'image accessible au chemin d'accès suivant :
        self.arriere_plan = pygame.image.load("assets/level/Background.png")

        self.vider_liste_element()

        # Créer des objets pièces grâce à l'attribut self.game_data
        type_pieces = self.game_data[difficulte][niveau - 1][1]
        coord_pieces = self.game_data[difficulte][niveau - 1][2]

        self.difficulte = difficulte
        self.niveau = niveau


        # Textes à afficher
        self.textes.append(self.police_niveau2.render(f"{self.difficulte}", True, (255, 255, 255)))
        self.textes.append(self.police_niveau1.render(f"niveau {self.niveau}", True, (255, 255, 255)))
        self.textes.append(self.police_niveau1.render(f"nombre de coups", True, (255, 255, 255)))
        self.textes.append(self.police_niveau1.render(f"Chronomètre", True, (255, 255, 255)))
        self.textes.append(self.police_niveau1.render(f"Score", True, (255, 255, 255)))

        #bouton retour
        bouton_retour = Bouton((140, 830), "assets/level/Bouton_Retour_Normal.png",
                               lambda: self.selection_level_menu(self.difficulte), None, self.button1_sound)


        self.boutons.add(bouton_retour)

        # Positions des textes
        self.textes_positions = [(140, 180), (140, 221), (140, 400), (1440, 180), (1440, 400)]

        for i in range(len(type_pieces)):
            x, y = coord_pieces[i]
            type_piece = type_pieces[i]
            if type_piece == 'Virus':
                nouvelle_piece = Piece(int(x), int(y), type_piece)
            else:
                nouvelle_piece = Piece(int(x), int(y), int(type_piece))

            self.pieces.add(nouvelle_piece)
            self.pieces.add(nouvelle_piece)

        self.etat_menu = 0
        self.autoriser_deplacement = True
        self.timer_debut_niveau = pygame.time.get_ticks()
        self.coups = 0
        self.score = 300

    def main_menu(self):
        # Charger l'image du menu principal

        menu_principal_image = pygame.image.load("assets/menus/main_menu/menu_principal.png").convert()

        # Mise à jour de l'arrière-plan
        self.arriere_plan = menu_principal_image
        self.top_layer_image = pygame.image.load("assets/level/Top_Layer_Background.png").convert_alpha()

        self.vider_liste_element()

        bouton_jouer = Bouton((771, 700), "assets/menus/main_menu/Bouton_Jouer_Normal.png", lambda: self.selection_difficulte_menu(),
                              None, self.button1_sound)
        bouton_quitter = Bouton((1065, 700), "assets/menus/main_menu/Bouton_Quitter_Normal.png", lambda: self.generer_event_quit(),
                                None, self.button1_sound)

        self.boutons.add(bouton_jouer)
        self.boutons.add(bouton_quitter)

        self.etat_menu = 1

    def selection_difficulte_menu(self):
        menu_selection_difficulte = pygame.image.load("assets/menus/selection_difficulte_menu/assets_corrompu/bottom_layer_rouge.png").convert()
        self.arriere_plan = menu_selection_difficulte

        self.vider_liste_element()


        bouton_difficulte = Bouton((0, 0), None,
                        lambda: self.selection_level_menu('Explorer.exe Débutant'), 'Débutant', self.button1_sound)
        bouton_retour = Bouton((39, 944), "assets/menus/victoire_menu/Bouton_Retour_Normal.png",
                               lambda: self.main_menu(), None, self.button1_sound)

        self.boutons.add(bouton_retour)
        self.boutons.add(bouton_difficulte)

        self.animation_en_cours = True

        self.etat_menu = 2

    def selection_level_menu(self, difficulte :str):
        menu_selection_level = pygame.image.load("assets/menus/selection_level_menu/Background.png").convert()
        self.arriere_plan = menu_selection_level

        self.vider_liste_element()

        chaine = difficulte
        affichage = chaine.split(' ')
        self.textes.append(self.police_niveau1.render(f"{affichage[0]}", True, (255, 255, 255)))
        self.textes.append(self.police_niveau1.render(f"{affichage[1]}", True, (255, 255, 255)))

        self.textes_positions = [(795, 122), (845, 169), #difficulté
                                 (906, 760), (959, 789), (913, 859), (906, 879), #niveau 1
                                 (521, 630), (574, 659), (528, 729), (521, 749), #niveau 2
                                 (1291, 627), (1344, 656), (1298, 726), (1291, 746), #niveau 3
                                 (210, 419), (263, 448), (217, 518), (210, 538),  # niveau 4
                                 (1602, 419), (1655, 448), (1609, 518), (1602, 538)]  # niveau 5



        position_bouton = [(863, 729), (478, 599), (1248, 596), (167, 388), (1559, 388)]

        for i, niveau in enumerate(self.game_data[difficulte]):
            if niveau[1] is not None:
                if niveau[3] != '00:00':
                    bouton_image = "assets/menus/selection_level_menu/Bouton_NivBleu_Normal.png"
                elif niveau[3]:
                    bouton_image = "assets/menus/selection_level_menu/Bouton_NivRou_Normal.png"
                bouton_level = Bouton(position_bouton[i], bouton_image,
                                      lambda difficulte=difficulte, i=i: self.lancer_niveau(difficulte, i + 1),
                                      None, self.button2_sound)

                self.textes.append(self.police_niveau2.render(f"Niveau", True, (255, 255, 255)))
                self.textes.append(self.police_niveau2.render(f"{i + 1}", True, (255, 255, 255)))
                self.textes.append(self.police_niveau3.render(f"score : {niveau[4]}", True, (255, 255, 255)))
                self.textes.append(self.police_niveau3.render(f"temps : {niveau[3]}", True, (255, 255, 255)))

                self.boutons.add(bouton_level)

        bouton_retour = Bouton((39, 944), "assets/menus/victoire_menu/Bouton_Retour_Normal.png",
                               lambda: self.selection_difficulte_menu(), None, self.button1_sound)
        self.boutons.add(bouton_retour)

        self.etat_menu = 3

    def victoire_menu(self):
        victoire_menu_image = pygame.image.load("assets/menus/victoire_menu/Background.png").convert()
        self.arriere_plan = victoire_menu_image

        self.vider_liste_element()

        if self.niveau < 5: #Il y a un maximum de 5 niveaux par difficulté
            if self.game_data[self.difficulte][self.niveau][1]: #vérifier que les pièces existent
                bouton_retour = Bouton((680, 540), "assets/menus/victoire_menu/Bouton_Retour_Normal.png",
                                    lambda: self.selection_difficulte_menu(), None, self.button1_sound)
                bouton_nivsuiv = Bouton((971, 540), "assets/menus/victoire_menu/Bouton_NivSuiv_Normal.png",
                                       lambda: self.lancer_niveau(self.difficulte, self.niveau+1), None, self.button1_sound)
                self.boutons.add(bouton_nivsuiv)

        else:
            bouton_retour = Bouton((825, 540), "assets/menus/victoire_menu/Bouton_Retour_Normal.png",
                                   lambda: self.selection_level_menu(self.difficulte), None, self.button1_sound)

        self.boutons.add(bouton_retour)


        # Textes à afficher
        self.textes.append(self.police_niveau2.render(f"Score : {self.score}", True, (255, 255, 255)))
        self.textes.append(self.police_niveau2.render(f"Temps : {self.minutes:02d}:{self.secondes:02d}", True, (255, 255, 255)))
        self.textes.append(self.police_niveau2.render(f"nombre de coups : {self.coups:02d}", True, (255, 255, 255)))

        # Positions des textes
        self.textes_positions = [(713, 382), (1012, 382), (765, 452)]

        self.game_data[self.difficulte][self.niveau - 1][3] = f"{self.minutes:02d}:{self.secondes:02d}"
        self.game_data[self.difficulte][self.niveau - 1][4] = self.score
        ecrire_csv('game_data.csv', self.game_data)


        self.etat_menu = 4

    def run(self):
        # Boucle principale du jeu
        while True:
            for evenement in pygame.event.get(): # Gestion des événements pygame
                if evenement.type == pygame.QUIT:
                    # Si l'utilisateur ferme la fenêtre, quitter le jeu
                    pygame.quit()
                    sys.exit()

                elif evenement.type == pygame.MOUSEBUTTONDOWN:
                    # Gestion des clics de souris
                    if self.etat_menu == 0 and self.autoriser_deplacement:
                        # Si le jeu est en cours et le déplacement est autorisé
                        self.gerer_clic_souris(evenement)
                        if self.piece_en_deplacement:
                            self.old_x, self.old_y = self.piece_en_deplacement.rect.x, self.piece_en_deplacement.rect.y

                    # Gestion des clics sur les boutons
                    for bouton in self.boutons:
                        if bouton.rect.collidepoint(evenement.pos) and bouton.est_pixel_non_transparent(*evenement.pos):
                            bouton.clic()

                elif evenement.type == pygame.MOUSEBUTTONUP:
                    # Gestion du relâchement du clic de souris
                    if self.etat_menu == 0 and self.autoriser_deplacement:
                        self.gerer_relachement_souris(self.old_x, self.old_y)

                elif evenement.type == pygame.MOUSEMOTION:
                    # Gestion du mouvement de la souris
                    if self.etat_menu == 0 and self.autoriser_deplacement:
                        self.gerer_mouvement_souris(evenement)
                    for bouton in self.boutons:
                        bouton.update_bouton()

                # Si la musique de niveau est en cours de lecture et qu'on est revenu au menu principal
                # Alors on joue la musique du menu
                if self.current_music == self.level_music and self.etat_menu != 0:
                    self.switch_to_menu_music()

                # Si la musique du menu est en cours de lecture et qu'on est passé au niveau
                # Alors on joue la musique du niveau
                elif self.current_music == self.menu_music and self.etat_menu == 0:
                    self.switch_to_level_music()

            # Vérification de la victoire et mise à jour de l'affichage
            self.verifier_victoire()
            self.afficher_fenetre()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def gerer_clic_souris(self, evenement):
        # Gestion du clic de souris sur les pièces
        for piece in self.pieces:
            if piece.rect.collidepoint(evenement.pos) and piece.est_pixel_non_transparent(*evenement.pos):
                self.pieces1_sound.play()
                self.piece_en_deplacement = piece
                self.creer_piece_groupe()
                self.decalage_x = piece.rect.x - evenement.pos[0]
                self.decalage_y = piece.rect.y - evenement.pos[1]

    def gerer_mouvement_souris(self, evenement):
        # Gestion du mouvement de la souris pour déplacer la pièce
        if self.piece_en_deplacement is not None:
            self.creer_piece_groupe()
            self.piece_en_deplacement.deplacer(
                evenement.pos[0] + self.decalage_x,
                evenement.pos[1] + self.decalage_y,
                self.axe_coord, self.pieces
            )

    def gerer_relachement_souris(self, old_x=None, old_y=None):
        # Gestion du relâchement de la souris
        if self.piece_en_deplacement is not None:
            self.piece_en_deplacement.force_position()
            if old_x and old_y:
                # Vérifier s'il y a eu un mouvement
                if old_x != self.piece_en_deplacement.rect.x and old_y != self.piece_en_deplacement.rect.y:
                    self.coups += 1

            if isinstance(self.piece_en_deplacement, Piece_groupe):
                # Gestion du relâchement pour les pièces groupées
                liste_piece = self.piece_en_deplacement.obtenir_liste_groupe_type()
                liste_positions = self.piece_en_deplacement.calculer_positions()
                liste_indexe = self.piece_en_deplacement.liste_indexe
                liste_piece_a_creer = []

                for piece in liste_piece:
                    liste_piece_a_creer.append(piece)

                indexe_a_parcourir = [0]
                for i in range(len(liste_indexe) - 1):
                    indexe_a_parcourir.append(indexe_a_parcourir[i] + liste_indexe[i])

                for i in range(len(indexe_a_parcourir)):
                    piece_a_creer = Piece(liste_positions[indexe_a_parcourir[i]][0], liste_positions[indexe_a_parcourir[i]][1],
                                          liste_piece_a_creer[i])
                    self.pieces.add(piece_a_creer)

                self.pieces.remove(self.piece_en_deplacement)
            self.piece_en_deplacement = None


    def afficher_fenetre(self):
        # Affichage de l'arrière-plan et du FPS
        self.fenetre.blit(self.arriere_plan, (0, 0))
        fps_texte = self.fps_font.render(f"FPS: {int(self.clock.get_fps())}", True, (0, 0, 0))
        self.fenetre.blit(fps_texte, (10, 10))

        # Gestion de l'affichage des boutons
        if self.etat_menu == 2 and self.animation_en_cours:
            self.lancer_animations(self.animation_images_SLM)
        elif self.etat_menu == 2 and not self.animation_en_cours:
            self.boutons.draw(self.fenetre)
        elif self.etat_menu in {1, 3, 4}:
            self.boutons.draw(self.fenetre)

        # Gestion de l'affichage des textes et mise à jour des variables du joueur
        if self.etat_menu == 0:
            self.pieces.draw(self.fenetre)
            self.fenetre.blit(self.top_layer_image, (0, 0))

            self.boutons.draw(self.fenetre)

            for i in range(len(self.textes)):
                self.fenetre.blit(self.textes[i], self.textes_positions[i])

            self.minutes, self.secondes = self.calculer_chrono()
            chronometre = self.police_niveau1.render(f"{self.minutes:02d}:{self.secondes:02d}", True, (255, 255, 255))
            self.fenetre.blit(chronometre, (1440, 221))

            coups = self.police_niveau1.render(f"{self.coups:02d}", True, (255, 255, 255))
            self.fenetre.blit(coups, (140, 441))

            self.update_score(self.minutes, self.secondes)
            score = self.police_niveau1.render(f"{self.score}", True, (255, 255, 255))
            self.fenetre.blit(score, (1440, 441))

        elif self.etat_menu in {3, 4}:
            for i in range(len(self.textes)):
                self.fenetre.blit(self.textes[i], self.textes_positions[i])

    def vider_liste_element(self):
        # Vidage des groupes et listes pour une nouvelle phase du jeu
        self.boutons.empty()
        self.pieces.empty()
        self.textes.clear()
        self.textes_positions.clear()

    def calculer_chrono(self):
        # Conversion des millisecondes en secondes
        duree_totale_ms = pygame.time.get_ticks() - self.timer_debut_niveau
        duree_totale_sec = duree_totale_ms // 1000

        # Calcul des minutes et secondes
        minutes = duree_totale_sec // 60
        secondes = duree_totale_sec % 60

        return minutes, secondes

    def update_score(self, minutes, secondes):
        # Mise à jour du score du joueur
        facteur_dict = {'Explorer.exe Débutant': 1, 'Kernel32 Avancé': 1.5, 'Regedit Expert': 2, 'System32 Maître': 2.5}
        facteur = facteur_dict[self.difficulte]

        temps_total_sec = minutes * 60 + secondes
        temps_accorde = self.calculer_temps_accorde()
        temps_de_depassement = max(temps_total_sec - temps_accorde, 0)
        points_perdus = int(temps_de_depassement * facteur)

        # Ajustement par tranche de 100
        points_perdus = max(0, points_perdus - (points_perdus % 100))

        self.score -= points_perdus
        self.score = max(self.score, 0)

    def calculer_temps_accorde(self):
        # Calcul du temps accordé en fonction de la difficulté
        temps_accorde_dict = {'Explorer.exe Débutant': 4, 'Kernel32 Avancé': 240, 'Regedit Expert': 300,
                              'System32 Maître': 360}
        return temps_accorde_dict[self.difficulte]

    def verifier_victoire(self):
        # Vérification de la victoire du joueur
        if self.etat_menu == 0 and self.autoriser_deplacement:
            for piece in self.pieces:
                if piece.type == 'Virus' and piece.rect.x == 600 and piece.rect.y == 100:
                    self.autoriser_deplacement = False
                    self.victoire_menu()

    def creer_piece_groupe(self):
        # Création d'un groupe de pièces si nécessaire
        if not isinstance(self.piece_en_deplacement, Piece_groupe):
            if self.piece_en_deplacement:
                self.pieces_deplacement = self.piece_en_deplacement.obtenir_piece_collision()
                if len(self.pieces_deplacement) > 1:
                    for piece in self.pieces:
                        if piece in self.pieces_deplacement:
                            self.pieces.remove(piece)

                    self.piece_en_deplacement.force_position()
                    self.piece_en_deplacement = Piece_groupe(self.pieces_deplacement)
                    self.pieces.add(self.piece_en_deplacement)

    def switch_to_level_music(self):
        # Arrêter la musique du menu
        self.menu_music.stop()
        # Jouer la musique de niveau
        self.level_music.play(loops=-1)
        # Mettre à jour la musique actuelle
        self.current_music = self.level_music

    def switch_to_menu_music(self):
        # Arrêter la musique de niveau
        self.level_music.stop()
        # Jouer la musique du menu
        self.menu_music.play(loops=-1)
        # Mettre à jour la musique actuelle
        self.current_music = self.menu_music

    def generer_event_quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))


# Entrée principale du programme
if __name__ == "__main__":
    antivirus = AntiVirus(1920, 1080)
    antivirus.run()